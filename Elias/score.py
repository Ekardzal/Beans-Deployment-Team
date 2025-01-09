import base64
import io
from io import BytesIO

import torch
from ultralytics import YOLO
from PIL import Image
import json
import os
import logging

# Initialisierung: YOLO-Modell laden
def init():
    global model
    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"),"YOLO-Model.pt")
    model = YOLO(model_path)  # YOLO-Modell laden
    # Sicherstellen, dass CPU verwendet wird
    if torch.cuda.is_available():
        torch.device("cpu")
    print("Model loaded successfully on CPU")

# Inferenz-Funktion
def run(raw_data):
    try:
        input_data = json.loads(raw_data)

        # Bilddaten dekodieren
        im_b64 = input_data["image"]
        im_bytes = base64.b64decode(im_b64)  # Base64 dekodieren
        img = Image.open(io.BytesIO(im_bytes))  # In PIL-Objekt umwandeln

        results = model(img)
        # Ergebnisse formatieren
        output = []
        for box in results[0].boxes.data:
            output.append({
                "x1": box[0].item(),
                "y1": box[1].item(),
                "x2": box[2].item(),
                "y2": box[3].item(),
                "confidence": box[4].item(),
                "class": int(box[5].item())
            })

        return json.dumps({"predictions": output})
    except Exception as e:
        return json.dumps({"error": str(e)})
