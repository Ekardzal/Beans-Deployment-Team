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
from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.standard_py_parameter_type import StandardPythonParameterType


errorlog = []
client = ImageAnalysisClient(endpoint="https://wayt-azureocr.cognitiveservices.azure.com/", credential=AzureKeyCredential("8bkM3LvovG72sEnfdZHZK0B30U0zdRtxAEEJipqZ1loIfHaoTDVNJQQJ99ALAC5RqLJXJ3w3AAAFACOGYosD"))
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

sample_input = StandardPythonParameterType({"image": "Image as Bytes String",})

sample_output = StandardPythonParameterType({"predictions": "Dictionary as Bytes String"})
@input_schema("datare", sample_input)
@output_schema(sample_output)
def incoming(datare):
    return

@rawhttp
def run(datarecieved): #funktioniert nur, wenn es data mit "image" gibt, dass zu einem image file decodet werden kann

    if (datarecieved.method == "POST"):
        try:

            json_result = []
            jsondict = {}
            recieved = json.loads(datarecieved.data)
            errorlog.append("request received")
            if recieved.get("image", None) is None:
                return AMLResponse("Request Timeout. The 'image' key is missing from the request.", 408)
            
            file_extension = f"{image.format}" if image.format in ["JPEG", "PNG"] else None

            if file_extension is None:
                errorlog.append(f"Unsupported media type: {file_extension or 'unknown'}")
                return AMLResponse("Unsupported Media Type. Only .jpg, .jpeg, and .png are supported.", 415)

            if not model:
                errorlog.append("Failed Dependency: Model not loaded")
                return AMLResponse("Failed Dependency. Model is not loaded.", 424)
            im_b64 = recieved["image"]
            im_bytes = base64.b64decode(im_b64)
            image = Image.open(io.BytesIO(im_bytes))
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
                cropped.save(byted, image.format)
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

            jsondict = {"predictions:":json_result}
            package = str.encode(json.dumps(jsondict))
            return AMLResponse(package, 200)
        except Exception as e:
            logging.debug(repr(e))
            return AMLResponse(("Internal Server Error. " + repr(e) + repr(errorlog)), 500)
        
    else:
        return AMLResponse("Invalid or Missing input.", 400)
