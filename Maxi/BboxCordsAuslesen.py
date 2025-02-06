'''
import os
from tokenize import String

def getBboxCords(dname:str, path:str) -> list:
    dname += ".txt"

    #prüfen, ob passende .txt in bestimmtem Verzeichnis vorhanden ist
    if dname in os.listdir(path):
        #print(dname + " konnte gefunden werden! Schreibt Koordinaten in Liste :D (hoffentlich)")

        #öffnet .txt Datei und liest einzelne Koordinaten aus
        os.chdir(path)
        datei = open(dname, 'r')
        lines = datei.read().split(" ")

        #schließen die .txt Datei wieder
        datei.close()

        #löscht erstes Element in Liste, weil das die Klasse ist (brauchen ja nur Koordinaten)
        lines.pop(0)

        #nimmt die string-Koordinaten und wandelt sie in floats um (in neu erstellter Liste in weiterer Liste)
        cords = [[]]
        for item in lines:
            cords[0].append(float(item))
        #print(cords)

        #gibt die Koordinaten als Liste zurück
        return cords
    else:
        print(dname + " konnte nicht gefunden werden..? :(")
'''

def txtToList(txtFile: str):

    bboxes = []
    class_labels = []

    # Mapping von Klassenwerten zu Namen
    label_mapping = {
        "0": "Dose1",
        "1": "Label"
    }
    try:
        #übergebene .txt öffnen
        with open(txtFile, "r") as file:
            #zeilenweise lesen
            for zeile in file:      #jede Iteration liefert Zeile als String
                #Zeilenumbrüche, Tabs und überflüssige Leerzeichen entfernen
                zeile = zeile.strip()
                #falls vorhanden, leere zeilen (zeile="") überspringen
                if not zeile:
                    continue

                #Zeile in Werte aufteilen (anhand von Leerzeichen)
                teile = zeile.split()

                #Klassenwert ersetzen
                class_label = label_mapping.get(teile[0], teile[0])
                # in Liste schreiben
                class_labels.append(class_label)

                #BBox-Koordinaten raussuchen
                #Elemente ab Index 1 werden in float-Zahl umgewandelt, welche wieder
                # in eine Liste geschrieben werden
                bbox = list(map(float, teile[1:]))
                bboxes.append(bbox)

         # **Debugging-Log hinzufügen**
        #print(f"Datei: {txtFile} - Anzahl Labels: {len(class_labels)}, Anzahl BBoxes: {len(bboxes)}")
        #print(f"Labels: {class_labels}")
        #print(f"BBoxes: {bboxes}")

        return class_labels, bboxes

    except FileNotFoundError:
        print("Die Datei wurde nicht gefunden.")
        return [], []
    except ValueError as e:
        print(f"Fehler beim Verarbeiten der Datei: {e}")
        return [], []

def listsToTxt(trsfLabels: list, trsfBBoxes: list, path: str):

    # Mapping von Namen zu Klassenwerten
    label_mapping = {
        "Dose1": "0",
        "Label": "1"
    }

    try:
        #erstellt an übergebenem path die aug_txt Datei
        with open(path, "w") as file:
            # mit der Funktion zip können iterierbare Objekte (bspw. Tupel und Listen) mittels deren Indexe zu Paaren zusammengefügt werden
            # wir itereren über die bei zip entstandenen Paare, um die Klassenbezeichnung von den entsprechenden BBox-Koordinaten zu trennen
            # die Schleife „holt“ bei jeder Iteration ein Tupel aus zip() und zerlegt es automatisch in die Variablen label und koordinaten
            for label, koordinaten in zip(trsfLabels, trsfBBoxes):
                #Klassenlabel zurück zu ursprünglichen Wert (0, 1) ersetzen
                orig_label = label_mapping.get(label, label)

                # Koordinaten in einen String umwandeln
                # koordinaten ist liste, geht davon jedes Element durch und schreibt es in String
                # k > aktueller Wert von koordinaten
                # join verbindet alle Iterables (mit einem Leerzeichen " " getrennt)
                koordinaten_str = " ".join(f"{k}" for k in koordinaten)

                # Zeile im Format "Klassenwert Koordinaten" erstellen (\n macht Zeilenumbruch)
                zeile = f"{orig_label} {koordinaten_str}\n"

                #zeile in Datei schreiben
                file.write(zeile)
        print(f"Die Datei wurde erfolgreich geschrieben: {path}")

    except Exception as e:
        print(f"Fehler beim Schreiben der Datei: {e}")