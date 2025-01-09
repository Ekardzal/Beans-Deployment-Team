from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from PIL import Image, ImageDraw
import os
from array import array
import sys
import time


def askAzureOCR (path):

    #Authentifizierung per Azure-Key

    subscription_key = os.environ["VISION_KEY"]
    endpoint = os.environ["VISION_ENDPOINT"]
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


    #Start Einlesen
    #Bild wird als Image Stream eingelesen

    print("======== AzureOCR-Prozess gestartet ========")
    image_path = path

    with open(image_path, "rb") as image_stream:
        start = time.time()
        # raw = True wird benötigt, wenn man Header-Infos braucht
        read_response = computervision_client.read_in_stream(image_stream, raw = True)
        # read_response liefert Dictionary mit "Operation-Location" als Key
        # daraus wird ID herausgelesen
        read_operation_location = read_response.headers["Operation-Location"]
        operation_id = read_operation_location.split("/")[-1]

        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(0.5)

        #Zeichnen initialisieren
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        #Rückgabeparameter initialisieren
        words = []
        positions = []
        probs = []

        if read_result.status == OperationStatusCodes.succeeded:
            end = time.time()
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    for word in line.words:
                        #print(f"- Wort: {word.text}, Position: {word.bounding_box}, Sicherheit: {word.confidence}")
                        #if line.text.lower() == "HomePOP".lower():
                        #print("HomePOP gefunden")
                        words.append(word.text)
                        positions.append(word.bounding_box)
                        probs.append(word.confidence)

                        # Kasten um Wort Zeichnen
                        draw.polygon(((word.bounding_box[0],word.bounding_box[1]),(word.bounding_box[2],word.bounding_box[3]),(word.bounding_box[4],word.bounding_box[5]),(word.bounding_box[6],word.bounding_box[7])), outline = "red", width=3)


        #image.show()
        duration = (end-start) * 10**3
        #print()
        #print("======= Lesen abgeschlossen =======")
        #print(f"Der Prozess hat {duration:.03f}ms gedauert")

        #Rückgabe
        return words, positions, probs, image, duration







