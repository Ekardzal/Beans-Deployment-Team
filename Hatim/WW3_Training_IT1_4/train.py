import multiprocessing
import os
os.environ["ULTRALYTICS_CALLBACKS_DISABLED"] = "neptune"

from ultralytics import YOLO
import neptune

from discord import send_discord_webhook


def start_neptune():
   pass


def on_train_start(trainer):
   print ("Start DES TRAININGS AAAAA")

def on_pretrain_routine_start_neptune(trainer) -> None:
    """Callback function called before the training routine starts."""
    global run
    run = neptune.init_run(
        project="beans-baustelle/Use-Case-Dose",
        name=run_name,
        tags=["augmented"],
        dependencies="infer",
        monitoring_namespace="monitoring"
    )
    run["parameters"] = params
    run["model/name"] = model_name
    run["imgcount"] = imgcount
    print("run gestartet")

    print("pretrain-routine started")

def on_train_epoch_end_neptune(trainer):
    metrics = trainer.metrics
    #epoch = trainer.epoch + 1  # Epoch count starts from 0
    for key, value in metrics.items():
        run[f"data/{key}"].append(value)

def on_fit_epoch_end(trainer) -> None:
    """Callback function called at end of each fit (train+val) epoch."""
    print("train-val-epoch ended")

def on_val_end(validator) -> None:
    """Callback function called at end of each validation."""
    print("validation completed")

def on_train_end_neptune(trainer):
    for file in os.listdir(trainer.save_dir):
        if file != "weights":
            run[file].upload(os.path.join(trainer.save_dir, file))
    #run["model"].upload(trainer.last)
    print(trainer.last)

    send_discord_webhook(
        webhook_url="https://discord.com/api/webhooks/1365301531032944640/kX_9Zl2_dAU390GVK3WEDg_8cuGDugYlK1ngUYKSGudRLt1WNPoKI1pbZB-a2hJddmR-",
        message=f"🎯 Training fertig! Parameter: {params}, {imgcount} Bilder",
        csv_path=trainer.csv,
        attach_csv=True  # False für Nur-Text
    )

    run.stop()

run_name = "yolo_it1_test"
dataset = "it1"
epochs = 2
learning_rate = 0.005
lrf = 0
imgcount = 2032  #8072
save_period = 20
optimizer = "adam"
params = {"learning_rate": learning_rate, "lrf": lrf, "name": run_name, "save_period" : save_period, "optimizer": optimizer, "epochs": epochs, "dataset": dataset}
#add cosine lr, AdamW/SGD, close-mosaic off-
model_name = "yolo11n-seg.pt"


model = YOLO(model_name)




if __name__ == "__main__":
    model.callbacks.pop("on_train_end")
    model.callbacks.pop("on_train_epoch_end")
    model.callbacks.pop("on_pretrain_routine_start")
    model.add_callback("on_train_epoch_end", on_train_epoch_end_neptune)
    model.add_callback("on_train_end", on_train_end_neptune)
    model.add_callback("on_pretrain_routine_start", on_pretrain_routine_start_neptune)

    results = model.train(device = "0", data = "config.yaml", lr0 = learning_rate, lrf = lrf, name = run_name, save_period = save_period, optimizer = optimizer, epochs = epochs)


