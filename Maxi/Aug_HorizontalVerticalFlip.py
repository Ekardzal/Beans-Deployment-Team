import cv2 #zum Speichern von Bildern
from PIL import Image, UnidentifiedImageError  # zum Bildeinlesen
import numpy as np #Bilder in NumPy-Arrays konvertieren
import albumentations as A
import os #für Verzeichnisse
from BboxCordsAuslesen import txtToList, listsToTxt

# Augmentation pipeline definieren
transform = A.Compose([
    A.HorizontalFlip(p=1),
    A.VerticalFlip(p=1)
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

# Path zu Ordner, in dem original Bilder und Labels liegen
origPath = r"D:\_WW_BeansBaustelle\Set2\ORIGINAL\img_lab"
# Path zu Ordner, in den augmentierte Bilder und Labels liegen sollen
augPath = r"D:\_WW_BeansBaustelle\Set2\AUGMENTATION\Rotation"

#geht jedes Bild (jpg oder png) im Verzeichnis durch
for i in os.listdir(origPath):
    if i.endswith(".jpg") or i.endswith(".png"):
        #speichert Pfad für einzelnes Bild ab
        image_path = os.path.join(origPath, i)

        try:
            #Albumentation erwartet Bild als Array mit nur 3 Kanälen (RGB, ohne Alpha/Transparenz)
            #Bild mittels Pillow laden und mit NumPy in Array konvertieren
            image = Image.open(image_path).convert("RGB") #Sicherstellen, dass es RGB ist
            image_array = np.array(image)
            #falls vorhanden, Alpha-Kanal entfernen
            if image_array.shape[-1] == 4:
                image_array = image_array[..., :3]

            # Array sicherstellen, dass es speichertechnisch kontinuierlich ist
            image_array = np.ascontiguousarray(image_array)

            #print(f"Bildform: {image_array.shape}, Datentyp: {image_array.dtype}")

            # falls Bilder nicht in uint8 vorliegen, konvertieren (sollten jedoch in uint8 vorliegen, da es entweder jpg oder png sind)
            if image_array.dtype != np.uint8:
                image_array = image_array.astype(np.uint8)
                #print(f"Bereinigte Form: {image_array.shape}, Typ: {image_array.dtype}")

            # entsprechende txt Datei suchen
            # dazugehörige BBox: Dateiname ohne .jpg/.png aber mit .txt
            orig_txt_file = os.path.splitext(i)[0] + ".txt"
            orig_txt_path = os.path.join(origPath, orig_txt_file)

            # prüfen, ob passende .txt im originalen Verzeichnis vorhanden ist
            if not os.path.exists(orig_txt_path):
                print(f"Text-Datei {orig_txt_path} zu entsprechendem Bild kann nicht gefunden werden.")

            #mittels Funktion txtToList BBoxen und Class_Labels aus txt bekommen
            liste_classLabels, liste_bboxes = txtToList(orig_txt_path)

            # **Prüfen, ob die Anzahl der Labels und BBoxes übereinstimmt**
            if len(liste_classLabels) != len(liste_bboxes):
                print(
                    f"Fehler: Anzahl Labels ({len(liste_classLabels)}) und BBoxes ({len(liste_bboxes)}) stimmen nicht überein für Datei {orig_txt_path}.")
                continue  # Wenn die Daten nicht übereinstimmen, überspringe dieses Bild

            # Transformation
            transformed = transform(image=image_array, bboxes=liste_bboxes, class_labels=liste_classLabels)
            transformed_image = transformed['image']
            transformed_bboxes = transformed['bboxes']
            transformed_class_labels = transformed['class_labels']

            # Transformiertes Bild von RGB zu BGR konvertieren (für OpenCV-Speicherung)
            transformed_image_bgr = cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR)

            # transformiertes Bild in Verzeichnis speichern
            trfImage = "aug_" + i
            transformed_path = os.path.join(augPath, trfImage)
            cv2.imwrite(transformed_path, transformed_image_bgr)
            print(f"Bild '{trfImage}' erfolgreich gespeichert.")

            # mittels Funktion listsToTxt die transformierten Labels und BBoxes im entsprechenden Verzeichnis in txt-Datei speichern
            augTxt_file = "aug_" + os.path.splitext(i)[0] + ".txt"
            augTxt_path = os.path.join(augPath, augTxt_file)
            listsToTxt(transformed_class_labels,transformed_bboxes,augTxt_path)


        except UnidentifiedImageError:
            print(f"Warnung: Das Bild '{image_path}' konnte nicht geladen werden.")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten bei '{image_path}': {e}")
