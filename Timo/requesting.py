from azure.ai.ml import MLClient
from azure.ai.ml.entities._inputs_outputs import output
from azure.identity import DefaultAzureCredential


#client = MLClient.from_config(credential=DefaultAzureCredential(), path="config.json")


import urllib.request
import json
import os
import ssl
from PIL import Image
import base64
import scoring

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
image = open("7a494d66-caf9-48c5-9cbd-33f73047ed53_Riedstrasse_16_09117_Chemnitz_Deutschland.png", "rb")
im64 = base64.b64encode(image.read()).decode("UTF-8")

data = {"image":im64,
        "ext":"PNG"}
body = str.encode(json.dumps(data))

url = 'https://end.westeurope.inference.ml.azure.com/score'
# Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
api_key = 'NLBHsesgjYRkev4IWqj0fASuXu3PlsVi'
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")


headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

req = urllib.request.Request(url, body, headers, method="POST")
print("requesting")
try:
    response = urllib.request.urlopen(req)
    print(repr(response))
    content =  response.read()
    jason = json.loads(content)
    print("recieved result: " + json.dumps(jason))

    out_file = open("example.json", "w")
    json.dump(jason, out_file, indent=2)

except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))