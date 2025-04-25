from azureml.contrib.services.aml_response import AMLResponse
import json
from PIL import Image  # Bildverarbeitung mit PIL
import base64  # Base64-Kodierung/-Dekodierung für Bilder
import io  # Ein-/Ausgabeoperationen
import logging

# Diese Methode ist sehr unsicher, bitte nur im run() Kontext mit rawhttp enabled nutzen
# sie wurde erstellt um den riesigen overhead zu handlen
# macht es auch einfacher neue checks einzuführen, ohne das scoring script zu bloaten
def CheckInput(input): 
    
    # Überprüfung, ob das Bild in der Anfrage enthalten ist
    if input.get("image", None) is None:
        return AMLResponse(("Request Timeout. The 'image' key is missing from the request." + repr(errorlog)), 408)

    if input["image"] is list:
        for package in input["image"]:
            file_extension = f"{package.format}" if package.format in ["JPEG", "PNG", "BMP", "WEBP", "TIFF", "JPG"] else None
            if file_extension is None:
                errorlog.append(f"Unsupported media type: {file_extension or 'unknown'}")
                return AMLResponse(("Unsupported Media Type. Only .jpg, .jpeg, .png, .bmp, .webp, and .tiff are supported." + repr(errorlog)), 415)

    file_extension = f"{input["image"].format}" if input["image"].format in ["JPEG", "PNG", "BMP", "WEBP", "TIFF", "JPG"] else None
    if file_extension is None:
        errorlog.append(f"Unsupported media type: {file_extension or 'unknown'}")
        return AMLResponse(("Unsupported Media Type. Only .jpg, .jpeg, .png, .bmp, .webp, and .tiff are supported." + repr(errorlog)), 415)

def Base64ToPILImage(bytes):
    im_bytes = base64.b64decode(bytes)  # Bild dekodieren
    image = Image.open(io.BytesIO(im_bytes))  # Bild in ein PIL-Image umwandeln

def InitiateLogger(destination) ->logging.Logger:
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG) # mein einziger Versuch dass was in den AzureML logs angezeigt wird
    logger.addHandler(logging.StreamHandler(stream=destination))