import os
from ultralytics import YOLO  # YOLO-Modell für Objekterkennung importieren
import json
import logging
from azureml.contrib.services.aml_request import AMLRequest, rawhttp  # AzureML Request Handling
from azureml.contrib.services.aml_response import AMLResponse  # AzureML Response Handling
from azure.ai.vision.imageanalysis import ImageAnalysisClient  # Azure OCR Client für Texterkennung
from azure.ai.vision.imageanalysis.models import VisualFeatures  # Visuelle Features für OCR-Analyse
from azure.core.credentials import AzureKeyCredential  # Azure-Authentifizierung
from PIL import Image  # Bildverarbeitung mit PIL
import base64  # Base64-Kodierung/-Dekodierung für Bilder
import io  # Ein-/Ausgabeoperationen
from io import BytesIO  # Verarbeitung von Byte-Daten
import methods
import logging

# Fehlerprotokoll-Liste
errorlog = []

# Azure OCR-Client initialisieren
client = ImageAnalysisClient(
    endpoint="https://tki-ocr.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("5bPFE4F0JoCKtTw4KDt0v0IySwSMWJYE5ExunGzbn7I8DIgv5loDJQQJ99BCACPV0roXJ3w3AAAFACOGtIHt")
)
errorlog.append("client registered.")

# Funktion zum Initialisieren des YOLO-Modells
def init():
    global model  # Globale Modellvariable
    try:
        model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "best.pt")  # Modellpfad ermitteln
        model = YOLO(model_path)  # YOLO-Modell laden
        errorlog.append("YOLO loaded.")
    except Exception as e:
        raise SystemExit # Ein Deployment ohne model/modelladefehler ist nutzlos, ich will dass es so schnell wie möglich scheitert

@rawhttp  # Funktion als raw HTTP-Handler definieren
def run(datarecieved):  # Verarbeitet HTTP-POST-Anfragen mit Bilddaten
    if (datarecieved.method == "POST"):
        try:

            json_result = []  # Ergebnisse speichern
            jsondict = {}
            recieved = json.loads(datarecieved.data)  # Eingehende JSON-Daten parsen
            methods.CheckInput(recieved)
            errorlog.append("request received")

            # Base64-dekodiertes Bild verarbeiten
            im_b64 = recieved["image"]  # Base64-kodiertes Bild aus JSON extrahieren

            
            if im_b64 is list:
                for image_b64 in im_b64:
                    image = image.append(methods.Base64ToPILImage(image_b64))
                    width, height = image_b64.size  # Bildgröße abrufen
                    errorlog.append(f"image loaded: {width}x{height}")
            else:
                image = methods.Base64ToPILImage(im_b64)
                width, height = image.size  # Bildgröße abrufen
                errorlog.append(f"image loaded: {width}x{height}")

            



            # Der YOLO Erkennungsprozess
            try:
                errorlog.append("Starting YOLO prediction...")
                results = model(image, stream=True)  # YOLO-Vorhersage ausführen
                errorlog.append("YOLO prediction completed successfully.")

                try:
                    json_result.append(json.loads(result[0].to_json()))  # Ergebnisse in JSON umwandeln
                    errorlog.append("YOLO results successfully converted to JSON.")
                except Exception as e:
                    errorlog.append(f"Error converting YOLO results to JSON: {repr(e)}")
                    return AMLResponse(("Internal Server Error: Failed to process YOLO results." + repr(errorlog)), 500)

            except Exception as e:
                errorlog.append(f"YOLO prediction failed: {repr(e)}")
                return AMLResponse(("Internal Server Error: YOLO prediction failed." + repr(errorlog)), 500)
            
            
            
            # Bounding Boxes extrahieren
            for result in results:
                boxing = result[0].boxes.xyxy
                for box in boxing:
                    errorlog.append("finding text...")
                    byted = BytesIO()
                    cropped = image.crop(box.tolist())  # Bereich mit Bounding Box ausschneiden
                    cropped.save(byted, image.format)  # Geschnittenes Bild speichern
                    imagebytes = byted.getvalue()
                
                    try:
                        # Azure OCR-Analyse für den Bereich durchführen
                        OCRresult = client.analyze(image_data=imagebytes, visual_features=[VisualFeatures.READ])
                    
                        # OCR-Ergebnisse verarbeiten
                        errorlog.append("dumping text in json")
                        json_result.append(OCRresult.as_dict())
                    
                    except Exception as e:
                        errorlog.append(f"OCR analysis failed: {repr(e)}")
                        return AMLResponse(("Failed to analyze the image for OCR. Please try again." + repr(errorlog)), 500)

            
                
            # Ergebnisse in JSON-Dictionary speichern
            jsondict = {"predictions": json_result,
                        "logs":}
            package = str.encode(json.dumps(jsondict))  # JSON in Bytes umwandeln
            return AMLResponse(package, 200)  # Erfolgreiche Antwort zurückgeben
        except Exception as e:
            logging.debug(repr(e))
            return AMLResponse(("Internal Server Error. " + repr(e) + repr(errorlog)), 500)  # Fehlerbehandlung
    else:
        return AMLResponse("Invalid or Missing input.", 400)  # Fehlermeldung für ungültige Anfragen
