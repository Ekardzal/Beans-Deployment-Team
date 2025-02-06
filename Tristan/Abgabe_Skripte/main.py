# importiert die ultralytics library ('pip install ultralytics' im Terminal notwendig)
from ultralytics import YOLO

# laedt ein Model, in diesem Fall ein neues ohne pre-training
model = YOLO("yolo11n.yaml")

# laedt ein Model, in diesem Fall ein Modell, das nach einem Trainingslauf weiter trainiert werden soll
# model = YOLO(r"path\to\last.pt")

# trainiert das Model, Angabe des Pfades zur .yaml-Datei
results = model.train(data=r"path\to\config\config.yaml", epochs=1)