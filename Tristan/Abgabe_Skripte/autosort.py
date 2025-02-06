from ultralytics import YOLO
import os
import csv
import shutil

model = YOLO(r"path\to\best.pt")                                                                           # Model laden

source = r"path\to\imagefolder"                                                                            # Quellordner, der die Bilder fuer die Prediction enthaelt

results = model(source, conf=0.59)                                                                         # Prediction-Befehl mit Confidence-Threshold von 0.59

sorted_results_dir = r"path\to\sorted"                                                                     # Output-Ordner der .csv-Datei
sorted_images_dir = r"path\to\sortedimages"                                                                # Output-Ordner der sortierten Bilder
os.makedirs(sorted_images_dir, exist_ok=True)                                                              # stellt sicher, dass das Verzeichnis existiert

detections = []                                                                                            # Liste um prediction-Ergebnisse zu speichern

for result in results: 
    result.save()                                                                                          # speichert die Ergbenisse (=Bilder mit Boundingbox)
    boxes = result.boxes.cpu().numpy()                                                                     # konvertiert BoundingBoxen ins NumPy-Format
    file_name = os.path.basename(result.path)                                                              # Dateinname extrahieren
    file_path = result.path                                                                                # speichert Dateipfad

    for box in boxes:
        x1,y1,x2,y2 = box.xyxy[0]                                                                          # extrahiert BoundingBox-Koordinaten
        confidence = box.conf[0]                                                                           # extrahiert Confidence-Wert
        class_id = int(box.cls[0])                                                                         # extrahiert Klassen-ID

    
        class_name = model.names[class_id]                                                                  #extrahiert Klassennamen aus dem Modell
        print(f"Box: {x1}, {y1}, {x2}, {y2}, Confidence: {confidence}, Class: {class_name}")

        detections.append((file_name,confidence, class_name, x1,y1,x2,y2))                                  # fuegt extrahierte Details in eine Liste zusammen

        confidence_bin = f"{int(confidence * 100 // 10) * 10}-{int(confidence * 100 // 10) * 10 + 10}%"     # erstellt die Confidence-Abstufungen-Ordner (60%-70%)
        bin_dir = os.path.join(sorted_images_dir, confidence_bin)
        os.makedirs(bin_dir, exist_ok=True)

        new_path = os.path.join(bin_dir,file_name)                                                          # verschiebt Bilder in die entsprechenden Ordner
        shutil.move(file_path, new_path)
        file_path=new_path


detections = sorted(detections, key=lambda x: x[0], reverse=True)                                           # sortiert nach Dateinnamen in absteigender Reihenfolge

csv_path = os.path.join(sorted_results_dir, "sorted_results.csv")                                           # speichert Ergebnisse in .csv-Datei
with open(csv_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["File Name", "Confidence", "Class", "X1", "Y1", "X2", "Y2"])
    writer.writerows(detections)

print(f"Sorted results saved to {csv_path}")                                                                # Speichermeldungen
print(f"Sorted images saved to {sorted_images_dir}")
