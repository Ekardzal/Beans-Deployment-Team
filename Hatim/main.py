from EasyOCR_test import askEasyOCR
from AzureOCR_test import askAzureOCR

path = "HandschriftBilder/message.png"

#  ===== EasyOCR ========
easyWords, easyPositions, easyProbs, easyImg, easyDuration = askEasyOCR(path)
easyFoundHomePop = False
easyHomePopProb = 0

for i in range(len(easyWords)):

    print(f"Wort: {easyWords[i]}")
    print(f"Position: {easyPositions[i]}")
    print(f"Sicherheit: {easyProbs[i]*100:0.03f}%")
    if easyWords[i].lower() == "HomePOP".lower():
        easyFoundHomePop = True
        easyHomePopProb = easyProbs[i]

#easyImg.show()
print(f"Dauer: {easyDuration:0.03f}ms")
print()

#  ===== AzureOCR ========
azureWords, azurePositions, azureProbs, azureImg, azureDuration = askAzureOCR(path)
azureFoundHomePop = False
azureHomePopProb = 0

for i in range(len(azureWords)):

    print(f"Wort: {azureWords[i]}")
    print(f"Position: {azurePositions[i]}")
    print(f"Sicherheit: {azureProbs[i]*100:0.03f}%")
    print("--------")

    if azureWords[i].lower() == "HomePOP".lower():
        azureFoundHomePop = True
        azureHomePopProb = azureProbs[i]

#azureImg.show()
print(f"Dauer: {azureDuration:0.03f}ms")
print()


#  ===== Vergleich ========
print("======== Ergebnisse ========")

    #Dauer vergleichen
if easyDuration < azureDuration:
    print (f"EASYOCR war {azureDuration-easyDuration:0.03f}ms schneller als AzureOCR ({((azureDuration-easyDuration)/azureDuration)*100:0.02f}%).")
elif easyDuration > azureDuration:
    print(f"AZUREOCR war {easyDuration - azureDuration:0.03f}ms schneller als EasyOCR({((easyDuration-azureDuration)/easyDuration)*100:0.02f}%).")
else:
    print("Wow, BEIDE waren gleich schnell o.o")
print(f"(EasyOCR: {easyDuration:0.03f}ms, AzureOCR: {azureDuration:0.03f}ms)")
print()

    #Sicherheit vergleichen
if easyHomePopProb > azureHomePopProb:
    print(f"EASYOCR war sich dabei {(easyHomePopProb-azureHomePopProb)*100:0.02f}% sicherer, HomePOP gelesen zu haben.")
elif easyHomePopProb < azureHomePopProb:
    print(f"AZUREOCR war sich dabei {(azureHomePopProb-easyHomePopProb)*100:0.02f}% sicherer, HomePOP gelesen zu haben.")
elif easyHomePopProb == azureHomePopProb == 0:
    print("BEIDE waren sich dabei gleich sicher, HomePOP NICHT gelesen zu haben.")
else:
    print("BEIDE waren sich dabei gleich sicher, HomePOP gelesen zu haben.")
print(f"(EasyOCR: {easyHomePopProb*100:0.02f}%, AzureOCR: {azureHomePopProb*100:0.02f}%)")
print()

    #HomePop gefunden?
if easyFoundHomePop:
    print("EasyOCR hat HomePOP erfolgreich erkannt.")
else:
    print("EasyOCR hat HomePOP nicht erkannt.")

if azureFoundHomePop:
    print("AzureOCR hat HomePOP erfolgreich erkannt.")
else:
    print("AzureOCR hat HomePOP nicht erkannt.")

if azureFoundHomePop and easyFoundHomePop:
    print("BEIDE haben HomePOP erkannt")
print()

    #Wer hat mehr Worte erkannt?
if len(easyWords) > len(azureWords):
    print(f"EasyOCR hat dabei {len(easyWords) - len(azureWords)} Wort(e) mehr erkannt.")
elif len(easyWords) < len(azureWords):
    print(f"AzureOCR hat dabei {len(azureWords) - len(easyWords)} Wort(e) mehr erkannt.")
else:
    print(f"Sie haben dabei gleich viele Worte erkannt: {len(easyWords)}")

print("============================")


#easyImg.show()
#azureImg.show()



