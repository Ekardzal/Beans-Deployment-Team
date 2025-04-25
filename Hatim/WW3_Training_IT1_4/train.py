from ultralytics import YOLO
from results_logger import log_results

run_name = "yolo_it1_aug_1"
learning_rate = 0.005
params = {"learning_rate": learning_rate, "lrf": 0.00001, "name": run_name, "save_period" : 20, "optimizer": "Adam", "epochs": 100, "dataset": "it1"}
path = f"runs/segment/{run_name}/results.csv"
model_name = "yolo11n-seg.pt"
model = YOLO(model_name)

if __name__ == "__main__":
    results = model.train(device = "0", data = "config.yaml", lr0 = 0.005, lrf = 0.00001, name = run_name, save_period = 20, optimizer = "adam")
    log_results(path, run_name, model_name, params)
