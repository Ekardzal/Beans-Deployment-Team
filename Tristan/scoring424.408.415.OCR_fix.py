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
import imghdr

errorlog = []
client = ImageAnalysisClient(
    endpoint=os.getenv("AZURE_OCR_ENDPOINT", "https://your-ocr-endpoint.cognitiveservices.azure.com/"),
    credential=AzureKeyCredential(os.getenv("AZURE_OCR_KEY", "your-ocr-key"))
)
errorlog.append("client registered.")

def init():
    global model
    try:
        model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "best.pt")
        model = YOLO(model_path)
        errorlog.append("YOLO loaded.")
    except Exception as e:
        model = None
        errorlog.append(f"Model loading failed: {repr(e)}")

@rawhttp
def run(datarecieved):
    if datarecieved.method == "POST":
        try:
            json_result = []
            recieved = json.loads(datarecieved.data)
            errorlog.append("request received")

            # Check for timeout (simulate 408 if no "image" key is found)
            if "image" not in recieved:
                errorlog.append("Request timeout: 'image' key missing")
                return AMLResponse("Request Timeout. The 'image' key is missing from the request.", 408)

            im_b64 = recieved["image"]
            im_bytes = base64.b64decode(im_b64)
            image = Image.open(io.BytesIO(im_bytes))

            # Validate file extension based on image content
            image_type = imghdr.what(None, h=im_bytes)
            file_extension = f".{image_type}" if image_type in ["jpeg", "png"] else None

            supported_formats = [".jpg", ".jpeg", ".png"]
            if file_extension not in supported_formats:
                errorlog.append(f"Unsupported media type: {file_extension or 'unknown'}")
                return AMLResponse("Unsupported Media Type. Only .jpg, .jpeg, and .png are supported.", 415)

            # Simulate 424 Failed Dependency if model is not loaded
            if not model:
                errorlog.append("Failed Dependency: Model not loaded")
                return AMLResponse("Failed Dependency. Model is not loaded.", 424)

            width, height = image.size
            errorlog.append(f"image loaded: {width}x{height}")

            errorlog.append("prediction result for image")
            result = model(image)
            json_result.append(json.loads(result[0].to_json()))
            errorlog.append("dumping results.")

            boxing = result[0].boxes.xyxy
            for box in boxing:
                errorlog.append("finding text...")
                byted = BytesIO()
                cropped = image.crop(box.tolist())
                cropped.save(byted, file_extension.lstrip("."))
                imagebytes = byted.getvalue()

                try:
                    OCRresult = client.analyze(image_data=imagebytes, visual_features=[VisualFeatures.READ])
                    OCR_lines = {
                        "lines": OCRresult.as_dict().get("lines", []),
                        "metadata": OCRresult.as_dict().get("metadata", {}),
                        "language": OCRresult.as_dict().get("language", None)
                    }
                    json_result.append(OCR_lines)
                    errorlog.append("dumping text in json")
                except Exception as e:
                    errorlog.append(f"OCR analysis failed: {repr(e)}")
                    return AMLResponse("Failed to analyze the image for OCR. Please try again.", 500)

            jsondict = {"predictions": json_result}
            package = json.dumps(jsondict).encode()
            return AMLResponse(package, 200)
        except Exception as e:
            logging.debug(repr(e))
            return AMLResponse(f"Internal Server Error: {repr(e)} {errorlog}", 500)

    else:
        return AMLResponse("Invalid or missing input", 400)
