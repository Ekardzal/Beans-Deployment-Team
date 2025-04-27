import csv


def log_results(path, run_name, model_name, params, imgcount):
    run = neptune.init_run(
        project="beans-baustelle/Use-Case-Dose",
        api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiI0YmUyNDM5Ny0zZjM5LTRkYmItOTc4MC05Yzg2YTE1Yzg1MzEifQ==",
        name=run_name,
        tags=["augmented"],
        dependencies="infer",
        monitoring_namespace="monitoring",
    )  # your credentials
    run["parameters"] = params
    run["model/name"] = model_name

    with open(path) as  f:
            reader = csv.reader(f, delimiter=",")
            next(reader)
            for epoch, line in enumerate(reader):
                run["data/time"].append(float(line[1]))
                run["data/train/box_loss"].append(float(line[2]))
                run["data/train/seg_loss"].append(float(line[3]))
                run["data/train/cls_loss"].append(float(line[4]))
                run["data/train/dfl_loss"].append(float(line[5]))
                run["data/metrics/precision(B)"].append(float(line[6]))
                run["data/metrics/recall(B)"].append(float(line[7]))
                run["data/metrics/mAP50(B)"].append(float(line[8]))
                run["data/metrics/mAP50-95(B)"].append(float(line[9]))
                run["data/metrics/precision(M)"].append(float(line[10]))
                run["data/metrics/recall(M)"].append(float(line[11]))
                run["data/metrics/mAP50(M)"].append(float(line[12]))
                run["data/metrics/mAP50-95(M)"].append(float(line[13]))
                run["data/val/box_loss"].append(float(line[14]))
                run["data/val/seg_loss"].append(float(line[15]))
                run["data/val/cls_loss"].append(float(line[16]))
                run["data/val/dfl_loss"].append(float(line[17]))
                run["data/lr/pg0"].append(float(line[18]))
                run["data/lr/pg1"].append(float(line[19]))
                run["data/lr/pg2"].append(float(line[20]))
    run["results"].upload(path)
    run["imgcount"] = imgcount
    run.stop()

