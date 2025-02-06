import os
from ultralytics import YOLO 
import json
import logging
from azureml.contrib.services.aml_request import AMLRequest, rawhttp
from azureml.contrib.services.aml_response import AMLResponse
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from PIL import Image
import base64
import io
from io import BytesIO
import urllib.request

errorlog = []
client = ImageAnalysisClient(endpoint="https://wayt-azureocr.cognitiveservices.azure.com/",
credential=AzureKeyCredential("8bkM3LvovG72sEnfdZHZK0B30U0zdRtxAEEJipqZ1loIfHaoTDVNJQQJ99ALAC5RqLJXJ3w3AAAFACOGYosD"))
clientstring = "client registered."
errorlog.append(clientstring)

def init():
    global model

    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "best.pt")
    model = YOLO(model_path)
    clientstring = "YOLO loaded."
    errorlog.append(clientstring)


@rawhttp
def run(datarecieved):  # funktioniert nur, wenn es data mit "image" gibt, dass zu einem image file decodet werden kann
    if datarecieved.method == "POST":
        try:
            json_result = []
            jsondict = {}
            recieved = json.loads(datarecieved.data)
            clientstring = "request recieved"
            errorlog.append(clientstring)

            # Check for timeout (simulate 408 if no "image" key is found)
            if "image" not in recieved:
                clientstring = "Request timeout: 'image' key missing"
                errorlog.append(clientstring)
                return AMLResponse("Request Timeout. The 'image' key is missing from the request.", 408)

            im_b64 = recieved["image"]
            im_bytes = base64.b64decode(im_b64)
            image = Image.open(io.BytesIO(im_bytes))

            # Check for supported formats
            supported_formats = [".jpg", ".jpeg", ".png"]
            file_extension = recieved.get("ext", "").lower()

            if file_extension not in supported_formats:
                clientstring = f"Unsupported media type: {file_extension}"
                errorlog.append(clientstring)
                return AMLResponse("Unsupported Media Type. Only .jpg, .jpeg, and .png are supported.", 415)

            # Simulate 424 Failed Dependency if model is not loaded
            if not model:
                clientstring = "Failed Dependency: Model not loaded"
                errorlog.append(clientstring)
                return AMLResponse("Failed Dependency. Model is not loaded.", 424)

            width, height = image.size
            clientstring = "image loaded." + repr(width) + "x" + repr(height)
            errorlog.append(clientstring)

            clientstring = "prediction result for image"
            errorlog.append(clientstring)
            result = model(image)
            json_result.append(json.loads(result[0].to_json()))
            clientstring = "dumping results."
            errorlog.append(clientstring)

            boxing = result[0].boxes.xyxy
            for box in boxing:
                clientstring = "finding text..."
                errorlog.append(clientstring)
                byted = BytesIO()
                cropped = image.crop(box.tolist())
                cropped.save(byted, file_extension.lstrip("."))  # Use the extension without the dot
                imagebytes = byted.getvalue()
                OCRresult = client.analyze(image_data=imagebytes, visual_features=[VisualFeatures.READ])

                # Filter OCR results to include only lines
                OCR_lines = {
                    "lines": OCRresult.as_dict().get("lines", []),
                    "metadata": OCRresult.as_dict().get("metadata", {}),
                    "language": OCRresult.as_dict().get("language", None)
                }
                json_result.append(OCR_lines)

                clientstring = "dumping text in json"
                errorlog.append(clientstring)

            jsondict = {"predictions:": json_result}
            package = str.encode(json.dumps(jsondict))
            return AMLResponse(package, 200)
        except Exception as e:
            logging.debug(repr(e))
            return AMLResponse(("Interner Serverfehler. " + repr(e) + repr(errorlog)), 500)

    else:
        return AMLResponse("Fehlende oder ungueltige Eingabe", 400)
