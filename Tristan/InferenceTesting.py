from ultralytics import YOLO
import os
import csv
from colorama import Fore, Back, Style
import base64

#region Variables
_inputModelPath = r"F:\Unii\GitHub\Beans-Deployment-Team\Tristan\best.pt"
_inputTestImagesPath = r"F:\Unii\GitHub\Beans-Deployment-Team\Tristan\input_small" 

_outputPredictionResultsPath = r"F:\Unii\GitHub\Beans-Deployment-Team\Tristan\output"
#endregion
#region Functions
def SaveToCSV(_outputPredictionResultsPath, _rawCSVData):
    csv_path = os.path.join(_outputPredictionResultsPath, "results.csv")
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["File Name", "Confidence", "Class", "Image"])
        writer.writerows(_rawCSVData)
    return True
#endregion

# Main
model = YOLO(_inputModelPath)

results = model.predict(_inputTestImagesPath, save=True, project=_outputPredictionResultsPath)

rawCSVData = []

for result in results: 
    _imageName = os.path.basename(result.path)
    _confidence = 0
    _class = ''

    _imageLink = '=IMAGE("' + result.path + '", "' + _imageName + '", 0)'

    boxes = result.boxes.cpu().numpy()

    for box in boxes:
        _confidence = str(box.conf[0]).replace(".", ",")
        _class = model.names[int(box.cls[0])]

        rawCSVData.append((_imageName, _confidence, _class, _imageLink))

    if _confidence == 0:
        rawCSVData.append((_imageName, _confidence, _class, _imageLink))

SaveToCSV(_outputPredictionResultsPath, rawCSVData)