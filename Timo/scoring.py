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

#error log wird zu debuggen genutzt
#ImageAnalaysisClient Klassenaufruf funktioniert nicht in init (glaube ich), deswegen außerhalb
errorlog = []
client = ImageAnalysisClient(endpoint="https://wayt-azureocr.cognitiveservices.azure.com/", credential=AzureKeyCredential("8bkM3LvovG72sEnfdZHZK0B30U0zdRtxAEEJipqZ1loIfHaoTDVNJQQJ99ALAC5RqLJXJ3w3AAAFACOGYosD"))
errorlog.append("client registered.")

#init() wird zum festlegen von globalen Variablen genutzt. In Azure wird Init als erste Funktion automatisch aufgerufen. Die Funktion ist zwingend Notwendig.
def init():
    global model
    try:
        model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "best.pt") #AZUREML_MODEL_DIR ist eine Default Enviroment Variable in Azure, und zeigt auf das folder vom ausgewählten Model. (wenn es z.B. in nem Unterordner innerhalb des Models ist dann ist der path "Unterordner/best.pt")
        model = YOLO(model_path) #YOLO modell wird initialisiert
        errorlog.append("YOLO loaded.")
    except Exception as e:
        model = None
        errorlog.append(f"Model loading failed: {repr(e)}")


#run() wird aufgerufen, sobald ein(e?) Payload mit einem korrekten API key an die API gesendet wird, mit dem Payload als Parameter. Die Funktion ist zwingend Notwendig.
@rawhttp
def run(datarecieved): #funktioniert nur, wenn es data mit "image" gibt, dass zu einem image file decodet werden kann (und mit der POST methode gesendet wurde)

    if (datarecieved.method == "POST"):
        try:

            json_result = []
            jsondict = {}
            recieved = json.loads(datarecieved.data) #payload wird geladen
            errorlog.append("request received")
            if recieved.get("image", None) is None: #kein key mit den name "image" wurde gefunden
                return AMLResponse("Request Timeout. The 'image' key is missing from the request.", 408)

            if not model: #die globale variable "model" ist "Null"
                errorlog.append("Failed Dependency: Model not loaded")
                return AMLResponse("Failed Dependency. Model is not loaded.", 424)
            im_b64 = recieved["image"]
            im_bytes = base64.b64decode(im_b64) #das Bild wird zum Bytes Objekt dekodiert, damit es von BytesIO gestreamt werden kann und dieser Stream von Pillow geöffnet werden kann
            image = Image.open(io.BytesIO(im_bytes))
            width, height = image.size

            file_extension = f"{image.format}" if image.format in ["JPEG", "PNG"] else None #file extention wird determiniert. Im Moment werden nur jpg/jpeg und PNG supportet weil das die gängigsten sind
                                                                                               #JPG = JPEG = jpeg
            if file_extension is None: #nicht JPEG oder PNG
                errorlog.append(f"Unsupported media type: {file_extension or 'unknown'}")
                return AMLResponse("Unsupported Media Type. Only .jpg, .jpeg, and .png are supported.", 415)
            errorlog.append(f"image loaded: {width}x{height}")
            
            

            errorlog.append("prediction result for image")
            result = model(image) #inference mit dem YOLO Modell
            json_result.append(json.loads(result[0].to_json())) #ergebnisse als json an json_result appended (to_json() ist ein string und kein dictionary!)
            errorlog.append("dumping results.")
            boxing = result[0].boxes.xyxy #xy Koordinaten der Bounding Boxen auf Koordinatensystem als TORCH TENSOR
            for box in boxing:
                errorlog.append("finding text...")
                byted = BytesIO()
                cropped = image.crop(box.tolist()) #.tolist() transformiert Torch Tensor zur Liste
                cropped.save(byted, image.format)
                imagebytes = byted.getvalue()
                
                try: #Inference mit Azure Vision (AzureOCR)
                    OCRresult = client.analyze(image_data=imagebytes, visual_features=[VisualFeatures.READ])
                    OCR_lines = {                                       #nur bestimmte Werte werden weitergegeben (um die größe der response zu reduzieren)
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
        except Exception as e: #irgend was unerwartetes ist passiert -> error log
            logging.debug(repr(e))
            return AMLResponse(("Internal Server Error. " + repr(e) + repr(errorlog)), 500)
        
    else: #hast du die POST methode verwendet?
        return AMLResponse("Invalid or Missing input.", 400)

