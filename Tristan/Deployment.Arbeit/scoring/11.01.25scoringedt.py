						
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
def run(datarecieved): #funktioniert nur, wenn es data mit "image" gibt, dass zu einem image file decodet werden kann
    if datarecieved.method == "POST":
        try:
            if model is None:
                return AMLResponse("Model is not loaded. Dependency failed.", 424)

            json_result = []
            jsondict = {}
            recieved = json.loads(datarecieved.data)
            clientstring = "request received"
            errorlog.append(clientstring)

            # Validate file type
            allowed_extensions = [".png", ".jpg", ".jpeg"]
            file_extension = recieved.get("ext", "").lower()

            if file_extension not in allowed_extensions:
                clientstring = f"Unsupported file type: {file_extension}"
                errorlog.append(clientstring)
                return AMLResponse(f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}", 400)

            # Decode the image
            try:
                im_b64 = recieved["image"]
                im_bytes = base64.b64decode(im_b64)
                image = Image.open(io.BytesIO(im_bytes))

                # Additional check: Ensure the MIME type matches allowed formats
                if image.format not in ["PNG", "JPEG"]:
                    clientstring = f"Image format {image.format} is not supported."
                    errorlog.append(clientstring)
                    return AMLResponse(f"Unsupported image format: {image.format}. Only PNG and JPEG are allowed.", 400)

                width, height = image.size
                clientstring = "image loaded." + repr(width) + "x" + repr(height)
                errorlog.append(clientstring)
            except Exception as image_error:
                clientstring = f"Image decoding failed: {repr(image_error)}"
                errorlog.append(clientstring)
                return AMLResponse("Image decoding dependency failed.", 424)

            # YOLO prediction
            try:
                clientstring = "prediction result for image"
                errorlog.append(clientstring)
                result = model(image)
                json_result.append(json.loads(result[0].to_json()))
                clientstring = "dumping results."
                errorlog.append(clientstring)
            except Exception as prediction_error:
                clientstring = f"Model prediction failed: {repr(prediction_error)}"
                errorlog.append(clientstring)
                return AMLResponse("Model prediction dependency failed.", 424)

            # Process bounding boxes and perform OCR
            try:
                boxing = result[0].boxes.xyxy
                for box in boxing:
                    clientstring = "finding text..."
                    errorlog.append(clientstring)
                    byted = BytesIO()
                    cropped = image.crop(box.tolist())
                    cropped.save(byted, recieved["ext"])
                    imagebytes = byted.getvalue()
                    OCRresult = client.analyze(image_data=imagebytes, visual_features=[VisualFeatures.READ])
                    json_result.append(OCRresult.as_dict())
                    clientstring = "dumping text in json"
                    errorlog.append(clientstring)
            except Exception as ocr_error:
                clientstring = f"OCR analysis failed: {repr(ocr_error)}"
                errorlog.append(clientstring)
                return AMLResponse("OCR dependency failed. Please check the input or the service.", 424)

            jsondict = {"predictions:": json_result}
            package = str.encode(json.dumps(jsondict))
            return AMLResponse(package, 200)

        except Exception as e:
            logging.debug(repr(e))
            return AMLResponse(("Dependency failed: " + repr(e) + repr(errorlog)), 424)

    else:
        return AMLResponse("Fehlende oder ungueltige Eingabe", 400)
