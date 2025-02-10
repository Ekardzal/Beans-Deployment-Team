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

# Fehlerprotokoll-Liste
errorlog = []

# Azure OCR-Client initialisieren
client = ImageAnalysisClient(
    endpoint="https://endpoint-d-ocr.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("CxcppgVbJYyNqF1T6fQSuQyzLzvrApNwcGSnEmIX6G4fdAxlxtVKJQQJ99BBACPV0roXJ3w3AAAFACOGJjE5")
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
        model = None  # Falls Fehler auftritt, Modell auf None setzen
        errorlog.append(f"Model loading failed: {repr(e)}")

@rawhttp  # Funktion als raw HTTP-Handler definieren
def run(datarecieved):  # Verarbeitet HTTP-POST-Anfragen mit Bilddaten
    if (datarecieved.method == "POST"):
        try:
            json_result = []  # Ergebnisse speichern
            jsondict = {}
            recieved = json.loads(datarecieved.data)  # Eingehende JSON-Daten parsen
            errorlog.append("request received")

            # Überprüfung, ob das Bild in der Anfrage enthalten ist
            if recieved.get("image", None) is None:
                return AMLResponse("Request Timeout. The 'image' key is missing from the request.", 408)

            # Überprüfung, ob das Modell geladen wurde
            if not model:
                errorlog.append("Failed Dependency: Model not loaded")
                return AMLResponse("Failed Dependency. Model is not loaded.", 424)

            # Base64-dekodiertes Bild verarbeiten
            im_b64 = recieved["image"]  # Base64-kodiertes Bild aus JSON extrahieren
            im_bytes = base64.b64decode(im_b64)  # Bild dekodieren
            image = Image.open(io.BytesIO(im_bytes))  # Bild in ein PIL-Image umwandeln
            width, height = image.size  # Bildgröße abrufen

            # Unterstützte Dateiformate prüfen
            file_extension = f"{image.format}" if image.format in ["JPEG", "PNG", "BMP", "WEBP", "TIFF", "JPG"] else None

            if file_extension is None:
                errorlog.append(f"Unsupported media type: {file_extension or 'unknown'}")
                return AMLResponse("Unsupported Media Type. Only .jpg, .jpeg, .png, .bmp, .webp, and .tiff are supported.", 415)
            
            errorlog.append(f"image loaded: {width}x{height}")
            
            try:
                errorlog.append("Starting YOLO prediction...")
                result = model(image)  # YOLO-Vorhersage ausführen
                errorlog.append("YOLO prediction completed successfully.")

                try:
                    json_result.append(json.loads(result[0].to_json()))  # Ergebnisse in JSON umwandeln
                    errorlog.append("YOLO results successfully converted to JSON.")
                except Exception as e:
                    errorlog.append(f"Error converting YOLO results to JSON: {repr(e)}")
                    return AMLResponse("Internal Server Error: Failed to process YOLO results.", 500)

            except Exception as e:
                errorlog.append(f"YOLO prediction failed: {repr(e)}")
                return AMLResponse("Internal Server Error: YOLO prediction failed.", 500)
            
            # Bounding Boxes extrahieren
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
                    json_result.append(OCRresult.as_dict())
                    errorlog.append("dumping text in json")
                except Exception as e:
                    errorlog.append(f"OCR analysis failed: {repr(e)}")
                    return AMLResponse("Failed to analyze the image for OCR. Please try again.", 500)

            # Ergebnisse in JSON-Dictionary speichern
            jsondict = {"predictions": json_result}
            package = str.encode(json.dumps(jsondict))  # JSON in Bytes umwandeln
            return AMLResponse(package, 200)  # Erfolgreiche Antwort zurückgeben
        except Exception as e:
            logging.debug(repr(e))
            return AMLResponse(("Internal Server Error. " + repr(e) + repr(errorlog)), 500)  # Fehlerbehandlung
    else:
        return AMLResponse("Invalid or Missing input.", 400)  # Fehlermeldung für ungültige Anfragen

