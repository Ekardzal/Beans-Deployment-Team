from ast import List
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import urllib.request
import json
import os
import ssl
import base64
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
        timeStart = time.time()
        print(f"attempt: {x+1} at {timing.TimeFormatted()}")
        if images is List:
            for image in images:
                timing.ClassifyImages(image, waitBetweenImages, timeStart)
        else:
            timing.ClassifyImages(images, waitBetweenImages, timeStart)
            


class timing:
    def ClassifyImages(image, waitBetweenImages: float, timeStart: float):
        print(f"image: {repr(image)} at {timing.TimeFormatted()}")
        time.sleep(waitBetweenImages)
        openImage = open(image, "rb")
        im64 = base64.b64encode(openImage.read()).decode("UTF-8")

        data = {"image":im64}
        body = str.encode(json.dumps(data))
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
        req = urllib.request.Request(url, body, headers, method="POST")

        print("requesting")
        try:
            response = urllib.request.urlopen(req)
            respString = repr(response.read())
            respString = respString[:20] #truncate to first 20
            print(f"{respString}, time taken: {'{:.2f}'.format(time.time() - timeStart)}s") #round floating point to 2 decimals
               
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))
        
        return

    def TimeStruct():
        return time.localtime(time.time())

    def TimeFormatted():
        return f"{timing.TimeStruct().tm_hour}:{timing.TimeStruct().tm_min}:{timing.TimeStruct().tm_sec}"


TestEndpoint("7a494d66-caf9-48c5-9cbd-33f73047ed53_Riedstrasse_16_09117_Chemnitz_Deutschland.png", 0, 60, 0) #4K Bild, insgesamt 9 Minuten
