import os

from ultralytics import YOLO
import neptune

from discord import send_discord_webhook

def on_pretrain_routine_start(trainer) -> None:
    """Callback function called before the training routine starts."""
    print("pretrain-routine started")

def on_train_epoch_end_neptune(trainer):
    metrics = trainer.metrics
    epoch = trainer.epoch + 1  # Epoch count starts from 0
    for key, value in metrics.items():
        run[f"data/{key}"].append(value)
    run["data/epoch"].append(epoch)

def on_fit_epoch_end(trainer) -> None:
    """Callback function called at end of each fit (train+val) epoch."""
    print("train-val-epoch ended")

def on_val_end(validator) -> None:
    """Callback function called at end of each validation."""
    print("validation completed")

def on_train_end_neptune(trainer):
    for file in os.listdir(trainer.save_dir):
        if file != "weights":
            run[f"{file}"].upload(f"{trainer.save_dir}/{file}")
    run["model"].upload(trainer.last)

    send_discord_webhook(
        webhook_url="https://discord.com/api/webhooks/1365301531032944640/kX_9Zl2_dAU390GVK3WEDg_8cuGDugYlK1ngUYKSGudRLt1WNPoKI1pbZB-a2hJddmR-",
        message=f"🎯 Training fertig! Parameter: {params}, {imgcount} Bilder",
        csv_path=trainer.csv,
        attach_csv=True  # False für Nur-Text
    )


run_name = "yolo_it1_test"
learning_rate = 0.005
imgcount = 2032  #8072
params = {"learning_rate": learning_rate, "lrf": 0, "name": run_name, "save_period" : 20, "optimizer": "Adam", "epochs": 1, "dataset": "it1"}
#add cosine lr, AdamW/SGD, close-mosaic off-
model_name = "yolo11n-seg.pt"

run = neptune.init_run(
        project="beans-baustelle/Use-Case-Dose",
        api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiI0YmUyNDM5Ny0zZjM5LTRkYmItOTc4MC05Yzg2YTE1Yzg1MzEifQ==",
        name=run_name,
        tags=["augmented"],
        dependencies="infer",
        monitoring_namespace="monitoring",
    )
run["parameters"] = params
run["model/name"] = model_name
run["imgcount"] = imgcount


model = YOLO(model_name)


model.reset_callbacks()
model.clear_callback("on_train_end")
model.clear_callback("on_train_epoch_end")
model.clear_callback("on_pretrain_routine_start")
model.add_callback("on_train_epoch_end", on_train_epoch_end_neptune)
model.add_callback("on_train_end", on_train_end_neptune)



if __name__ == "__main__":
    results = model.train(device = "0", data = "config.yaml", lr0 = learning_rate, lrf = 0, name = run_name, save_period = 20, optimizer = "adam", epochs = 1)


run.stop()