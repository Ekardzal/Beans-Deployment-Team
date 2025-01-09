from EasyOCR_test import askEasyOCR
from AzureOCR_test import askAzureOCR
from toCsv import toCsv
import os

directory = "HandschriftBilder"
path = "Bilder/00.jpg"

img_list = []

az_speed_list = []
az_prob_list = []
az_word_list = []

easy_speed_list = []
easy_prob_list = []
easy_word_list = []


for filename in os.listdir(directory):
    path = os.path.join(directory, filename)
    print(f"Bearbeite Datei {filename}")
    easyWords, easyPositions, easyProbs, easyImg, easyDuration = askEasyOCR(path)
    azureWords, azurePositions, azureProbs, azureImg, azureDuration = askAzureOCR(path)

    img_list.append(filename)

    az_speed_list.append(azureDuration/10**3)
    if len(azureWords) > 0:
        az_prob_list.append(sum(azureProbs)/len(azureProbs))
    else:
        az_prob_list.append(0)
    az_word_list.append(len(azureWords))

    easy_speed_list.append(easyDuration/10**3)
    if len(easyWords) > 0:
        easy_prob_list.append(sum(easyProbs)/len(easyProbs))
    else:
        easy_prob_list.append(0)
    easy_word_list.append(len(easyWords))


toCsv(img_list, az_speed_list, az_prob_list, az_word_list, "AzureOCR")
toCsv(img_list, easy_speed_list, easy_prob_list, easy_word_list, "EasyOCR")
print("fertig")