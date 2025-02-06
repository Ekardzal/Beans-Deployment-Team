import cv2 #zum Speichern von Bildern
from PIL import Image, UnidentifiedImageError  # zum Bildeinlesen
import numpy as np #Bilder in NumPy-Arrays konvertieren
import albumentations as A
import os #für Verzeichnisse

#einzelne Augmentation definieren
'''
#Grün-Stich

transform = A.RGBShift(
    r_shift_limit=0,
    g_shift_limit=(29, 30),
    b_shift_limit=0,
    p=1
)
'''
#Blau-Stich

transform = A.RGBShift(
    r_shift_limit=0,
    g_shift_limit=0,
    b_shift_limit=(29, 30),
    p=1
)
'''
#Rot-Stich

transform = A.RGBShift(
    r_shift_limit=(29,30),
    g_shift_limit=0,
    b_shift_limit=0,
    p=1
)
'''
# Path zu Ordner, in dem original Bilder und Labels liegen
origPath = r"C:\Users\maxir\OneDrive\Desktop\BeansBaustelle\IA_Test\img_lab"
# Path zu Ordner, in den augmentierte Bilder und Labels liegen sollen
augPath = r"C:\Users\maxir\OneDrive\Desktop\BeansBaustelle\IA_Test\aug\BlauStich"

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

            print(f"Bildform: {image_array.shape}, Datentyp: {image_array.dtype}")

            if image_array.dtype != np.uint8:
                image_array = image_array.astype(np.uint8)
                print(f"Bereinigte Form: {image_array.shape}, Typ: {image_array.dtype}")

            #Transformation
            transformed = transform(image=image_array)
            transformed_image = transformed['image']

            # Transformiertes Bild von RGB zu BGR konvertieren (für OpenCV-Speicherung)
            transformed_image_bgr = cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR)

            #transformiertes Bild in Verzeichnis speichern
            trfImage = "aug_" + i
            transformed_path = os.path.join(augPath, trfImage)
            cv2.imwrite(transformed_path, transformed_image_bgr)
            print(f"Bild '{trfImage}' erfolgreich gespeichert.")

            #unverändertes Label/BBox als entsprechende .txt abspeichern
            #dazugehörige BBox: Dateiname ohne .jpg aber mit .txt
            orig_txt_file = os.path.splitext(i)[0] + ".txt"
            orig_txt_path = os.path.join(origPath, orig_txt_file)

            #prüfen, ob passende .txt im Verzeichnis vorhanden ist
            if os.path.exists(orig_txt_path):
                #Datei öffnen und Inhalt rausschreiben
                file = open(orig_txt_path, 'r')
                content = file.read()
                file.close()

                #BBox im Zielverzeichnis in neue .txt schreiben
                aug_txt_file = "aug_" + os.path.splitext(i)[0] + ".txt"
                aug_txt_path = os.path.join(augPath, aug_txt_file)

                file = open(aug_txt_path, 'w')
                file.write(content)
                file.close()
                print(f"Labels/BBox als '{aug_txt_file}' erfolgreich gespeichert.")
                print("-------------------------")
            else:
                print(f"Keine passende Textdatei für '{i}' gefunden.")

        #Fehlermeldung von PIL wenn Bild beschädigt/nicht lesbar
        except UnidentifiedImageError:
            print(f"Warnung: Das Bild '{image_path}' konnte nicht geladen werden.")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten bei '{image_path}': {e}")
