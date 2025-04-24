from ultralytics import YOLO  # YOLO-Modell für Objekterkennung importieren
import json
from azureml.contrib.services.aml_request import AMLRequest, rawhttp  # AzureML Request Handling
from azureml.contrib.services.aml_response import AMLResponse  # AzureML Response Handling
from azure.ai.vision.imageanalysis import ImageAnalysisClient  # Azure OCR Client für Texterkennung
from azure.ai.vision.imageanalysis.models import VisualFeatures  # Visuelle Features für OCR-Analyse
from azure.core.credentials import AzureKeyCredential  # Azure-Authentifizierung
from io import BytesIO  # Verarbeitung von Byte-Daten
from PIL import Image

# Fehlerprotokoll-Liste
errorlog = []

# Azure OCR-Client initialisieren
client = ImageAnalysisClient(
    endpoint="https://tki-ocr.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("5bPFE4F0JoCKtTw4KDt0v0IySwSMWJYE5ExunGzbn7I8DIgv5loDJQQJ99BCACPV0roXJ3w3AAAFACOGtIHt")
)
errorlog.append("client registered.")

# Funktion zum Initialisieren des YOLO-Modells

global model  # Globale Modellvariable
try:
    model_path = "best.pt"  # Modellpfad ermitteln
    model = YOLO(model_path)  # YOLO-Modell laden
    errorlog.append("YOLO loaded.")
except Exception as e:
    model = None  # Falls Fehler auftritt, Modell auf None setzen
    errorlog.append(f"Model loading failed: {repr(e)}")

class compare:
    def classify(image):
        json_result = []
        result = model(image)
        json_result.append(json.loads(result[0].to_json()))
        boxing = result[0].boxes.xyxy
        for box in boxing:
            print("finding text...")
            byted = BytesIO()
            image = Image.open("7a494d66-caf9-48c5-9cbd-33f73047ed53_Riedstrasse_16_09117_Chemnitz_Deutschland.png")
            cropped = image.crop(box.tolist())  # Bereich mit Bounding Box ausschneiden
            cropped.save(byted, image.format)  # Geschnittenes Bild speichern
            imagebytes = byted.getvalue()
                
            try:
                # Azure OCR-Analyse für den Bereich durchführen
                OCRresult = client.analyze(image_data=imagebytes, visual_features=[VisualFeatures.READ])
                    
                # OCR-Ergebnisse verarbeiten
                print("dumping text in json")
                json_result.append(OCRresult.as_dict())
                    
            except Exception as e:
                print(f"OCR analysis failed: {repr(e)}")
        json_result = json_result[:20]
        print(repr(json_result))
        return


for x in range(60):
    compare.classify("7a494d66-caf9-48c5-9cbd-33f73047ed53_Riedstrasse_16_09117_Chemnitz_Deutschland.png")