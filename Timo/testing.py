import string
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import urllib.request
import json
import os
import ssl
from PIL import Image
import base64
import scoring
import time

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

url = 'https://endpunkt-mjyxx.germanywestcentral.inference.ml.azure.com/score'
# Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
api_key = 'EOLqlbiHInFPB2qj5s7L0mqZHWvxOnoASrgub3odRS3tpaTuhoN0JQQJ99BCAAAAAAAAAAAAINFRAZML3lyt'
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")






def TestEndpoint(images, waitBetweenImages: float, tries: int, waitBetweenTries: float):
    for x in range(tries):
        time.sleep(waitBetweenTries)
        timeNow = time.localtime(time.time())
        print(f"attempt: {x} at {timeNow.tm_hour}:{timeNow.tm_min}:{timeNow.tm_sec}")
        for image in images:
            timeNow = time.localtime(time.time())
            print(f"image: {repr(image)} at {timeNow.tm_hour}:{timeNow.tm_min}:{timeNow.tm_sec}")
            time.sleep(waitBetweenImages)
            openImage = open(image, "rb")
            im64 = base64.b64encode(openImage.read()).decode("UTF-8")

            data = {"image":im64,
                     "ext":"JPEG"}
            body = str.encode(json.dumps(data))
            headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
            req = urllib.request.Request(url, body, headers, method="POST")

            print("requesting")
            try:
                response = urllib.request.urlopen(req)
                respString = repr(response.read())
                respString = respString[:20]
                print(respString)
               
            except urllib.error.HTTPError as error:
                print("The request failed with status code: " + str(error.code))

                # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
                print(error.info())
                print(error.read().decode("utf8", 'ignore'))

TestEndpoint(["0b17ca4e-b71d-491d-b1ab-36b6943f41c0.jpg", "0b17ca4e-b71d-491d-b1ab-36b6943f41c0.jpg"], 0, 60, 0)