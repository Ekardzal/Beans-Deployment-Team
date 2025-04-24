import os

import cv2
import matplotlib.pyplot as plt
import neptune
from ultralytics import YOLO

project = neptune.init_project(project="beans-baustelle/Use-Case-Dose", api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiIzN2FiOWI5ZC1iNGNiLTQ5NTEtYjMyYS03ZGJjNGZhOWZkMDYifQ==")

def init_run(tags=None):
   run = neptune.init_run(
       project="beans-baustelle/Use-Case-Dose", 
       api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiIzN2FiOWI5ZC1iNGNiLTQ5NTEtYjMyYS03ZGJjNGZhOWZkMDYifQ==",
       tags=tags,
   )
   return run

MODEL_NAME= r"C:\Users\admin\Desktop\detect\wwww\yolo11-seg_it1.5.pt"

model = YOLO(MODEL_NAME)

run = init_run(['yolo-detection'])

run["model/task"] = model.task
run["model/name"] = MODEL_NAME

img_path = "C:/Users/admin/Desktop/newrun/"


results = model(img_path)

for i, result in enumerate(results):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(cv2.cvtColor(result.plot(), cv2.COLOR_BGR2RGB))
    ax.axis("off")
    run[f"predictions/images/image_{i}"].upload(neptune.types.File.as_image(fig))
    plt.close(fig)


plt.show()

