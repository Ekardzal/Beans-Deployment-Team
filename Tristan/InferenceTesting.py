from ultralytics import YOLO
import os
import csv
from colorama import Fore, Back, Style

#region Variables
_inputModelPath = r"F:\Unii\AAAAAAA\best.pt"
_inputTestImagesPath = r"F:\Unii\GitHub\Beans-Deployment-Team\Tristan\input" 

_outputPredictionResultsPath = r"F:\Unii\GitHub\Beans-Deployment-Team\Tristan\output"
#endregion
#region Functions
def SaveToCSV(_outputPredictionResultsPath, _rawCSVData):
    csv_path = os.path.join(_outputPredictionResultsPath, "results.csv")
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["File Name", "Confidence", "Class"])
        writer.writerows(_rawCSVData)
    return True
#endregion

# Main
model = YOLO(_inputModelPath)

results = model.predict(_inputTestImagesPath, save=True, project=_outputPredictionResultsPath)

rawCSVData = []

for result in results: 
    _imageName = os.path.basename(result.path)
    for box in result.boxes.cpu().numpy():
        _confidence = str(box.conf[0]).replace(".", ",")
        _class = model.names[int(box.cls[0])]
        print(_imageName + _class + _confidence)

        rawCSVData.append((_imageName, _confidence, _class))

SaveToCSV(_outputPredictionResultsPath, rawCSVData)



