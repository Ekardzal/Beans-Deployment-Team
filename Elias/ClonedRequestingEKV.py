import json
import base64
import urllib.request
import os

# Funktion zum Laden und Kodieren eines Bildes
def encode_image(image_path):
    """
    Liest ein Bild und kodiert es in Base64.
    :param image_path: Pfad zum Bild.
    :return: Base64-kodiertes Bild als String.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Bildpfad (aktualisiere diesen mit dem Pfad zu deinem Bild)
image_path = "Test_PNG_Dose.png"
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")

# Base64-kodiertes Bild
encoded_image = encode_image(image_path)

# Daten für die Anfrage
data = {
    "image": encoded_image,  # Base64-kodiertes Bild
    "ext": "png"            # Bildformat (aktualisiere, falls nötig)
}
body = json.dumps(data).encode("utf-8")

# Endpoint-URL (ersetze mit deinem tatsächlichen Endpoint)
url = "https://test-kaivl.germanywestcentral.inference.ml.azure.com/score"

# API-Schlüssel (ersetze mit deinem tatsächlichen Schlüssel)
api_key = '4eJ61Gxpz4oAqxUWfEzYcuxaxcydAC8R'
if not api_key:
    raise ValueError("Fehlender API-Schlüssel!")

# Header für die Anfrage
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Anfrage senden
try:
    print("Sende Anfrage an den Endpoint...")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        response_content = response.read().decode("utf-8")
        response_json = json.loads(response_content)
        print("Antwort vom Endpoint:")
        print(json.dumps(response_json, indent=4))  # Schön formatierte JSON-Ausgabe
except urllib.error.HTTPError as e:
    print(f"HTTP-Fehler: {e.code}")
    print(e.read().decode("utf-8"))
except urllib.error.URLError as e:
    print(f"URL-Fehler: {e.reason}")
except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
