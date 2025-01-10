import urllib.request
import json
import os
import ssl
import base64
import time
from PIL import Image

def allow_self_signed_https(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allow_self_signed_https(True)

URL = 'https://end.westeurope.inference.ml.azure.com/score'
API_KEY = 'NLBHsesgjYRkev4IWqj0fASuXu3PlsVi'
HEADERS = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + API_KEY)}

INPUT_FOLDER = "./image_inputs"
OUTPUT_FOLDER = "./json_outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def send_request(image_path):
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("UTF-8")
    
    data = {"image": image_base64, "ext": os.path.splitext(image_path)[1][1:].upper()}
    body = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(URL, body, HEADERS, method="POST")
    try:
        start_time = time.time()
        response = urllib.request.urlopen(request)
        response_time = time.time() - start_time
        result = json.loads(response.read())
        result["response_time"] = response_time
        return result, True
    except urllib.error.HTTPError as error:
        error_message = {
            "error_code": error.code,
            "error_message": error.read().decode("utf-8", "ignore"),
        }
        return error_message, False

def process_images():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            image_path = os.path.join(INPUT_FOLDER, filename)
            print(f"Processing: {filename}")

            result, success = send_request(image_path)

            status = "success" if success else "error"
            output_filename = f"{os.path.splitext(filename)[0]}_{status}.json"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            with open(output_path, "w", encoding="utf-8") as output_file:
                json.dump(result, output_file, indent=2)

            if success:
                print(f"  -> Success: Response time = {result['response_time']:.2f} seconds. Saved result to {output_filename}")
            else:
                print(f"  -> Error: Saved error details to {output_filename}")

if __name__ == "__main__":
    process_images()