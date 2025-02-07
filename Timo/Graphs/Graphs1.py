import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt
import csv
#------------------------------------------------------------------------------------------------------------#
#Das ist ein script, das mit matplotlib nacheinander Graphen generiert. um den nächsten zu sehen, musst der alte geschlossen werden.
#Das Fenster, in dem der Graph generiert wird hat verschiedene Funktionen, unter anderem das Resizen vom Viewport(das Fenster) und das abspeichern.
#die Graphen sind mit Bindestrichen abgetrennt.
#Weitere Graphen in sprinting.py
#------------------------------------------------------------------------------------------------------------#
# öffnen und auslesen eines CSV files, wobei die werte in der 2. Reihe sind und alles, was nicht ein "Wert" (z.B. String) ist ignoriert wird und zur nächsten Zeile gesprungen wird
con = []
with open("trainingresults\preAugRES\smallset30.aug\sorted_results.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            con.append(float(row[1]))
        except ValueError:
            continue
print(con)


average_heller = np.average((con[0], con[12]))
average_gruen = np.average((con[1], con[7], con[13], con[18]))
average_dunkler = np.average((con[2], con[8], con[14], con[19]))
average_blur = np.average((con[3], con[9], con[15], con[20]))
average_blau = np.average((con[4], con[10], con[16], con[21]))
average_normal = np.average((con[5], con[11], con[17], con[22]))
label_container = ["normal", "heller (n = 2)", "dunkler", "blur", "gruen", "blau"]
value_container = [average_normal, average_heller, average_dunkler, average_blur, average_gruen, average_blau]
color_container = ["#004e9e", "#4a9edd", "#003366", "#72A0C1", "tab:green", "#004e9e"]
#vergleichen von verschiedenen prediction ergebnissen auf augmentation (Säulendiagramm)
fig, ax = plt.subplots()
bar_container = ax.bar(label_container,
       value_container,
       color=color_container)
ax.bar_label(bar_container, fmt="{:.3f}")
ax.set_ylim(0.7, 1)
ax.set_yticks(np.arange(0.7, 1, 0.03))
ax.set_ylabel("confidence")
ax.set_title("Durchschnittliche Confidence je Augmentierungsart\nVerwendete Bilder je Augmentierungsart: 4")
#fig.set_size_inches(8.5, 5) #für einen besseren viewport falls gebraucht
plt.show()
del con, fig, ax
#------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------------------------#
#auslesen von mehreren CSV files zum verwerten
con_noAug = []
with open("trainingresults/preAugRES/fullset452.NOaug/sorted_results.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            con_noAug.append(float(row[1]))
        except ValueError:
            continue

con_10epoch = []
with open("trainingresults/10epochs/fullset452.NOaug/sorted_results.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            con_10epoch.append(float(row[1]))
        except ValueError:
            continue

con_20epoch = []
with open("trainingresults/20epochs/fullset452.NOaug/sorted_results.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            con_20epoch.append(float(row[1]))
        except ValueError:
            continue

avg_conNo = np.average(con_noAug)
avg_con10 = np.average(con_10epoch)
avg_con20 = np.average(con_20epoch)

#plotten eines Liniendiagramms zum vergleich verschiedener Epochen
fig, ax = plt.subplots()
ax.plot(("keine Augmentation", "Augmentation 10 Epochen", "Augmentation 20 Epochen"), (avg_conNo, avg_con10, avg_con20), "bo", linestyle="-")
ax.set_ylim(0.7, 1)
ax.set_yticks(np.arange(0.7, 1, 0.03))
ax.set_ylabel("confidence")
ax.set_title("Durchschnittliche Confidence pro Trainingsabschnitt ")
fig.set_size_inches(7, 5)
plt.show()

del fig, ax
#------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------------------------#
#unorthodoxes plotten eines "stacked" Histogramms -> Matplotlib hat dafür schon eine Funktion (die ich nicht nutze)
fig, ax = plt.subplots()
ax.hist(con_noAug, label="keine Augmentation", color="#004e9e")
ax.hist(con_10epoch, alpha=0.9, label="Augmentation 10 Epochen", color="tab:orange")
ax.hist(con_20epoch, label="Augmentation 20 Epochen", color="tab:green")
ax.set_ylabel("Anzahl Bilder")
ax.set_xlabel("Confidence")
ax.set_title("Histogramme Confidences verschiedener Modelle")
ax.legend()
plt.show()

del fig, ax
#------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------------------------#
#splitten des Histogramms auf mehrere Diagramme (weil für Farbenblinde schwer auslesbar)
fig, (ax, bx) = plt.subplots(1, 2, sharex=True)
ax.hist(con_noAug, label="keine Augmentation", color="#004e9e")

bx.hist(con_20epoch, label="Augmentation 20 Epochen", color="tab:green")
ax.set_ylabel("Anzahl Bilder")
ax.set_xlabel("Confidence")
bx.set_ylabel("Anzahl Bilder")
bx.set_xlabel("Confidence")
ax.set_title("Histogramm Confidences ohne Augmentation")
bx.set_title("Histogramm Confidences 20 Epochen")
fig.suptitle("Histogramme verschiedener Trainingsabschnitte")
fig.set_size_inches(10, 5)
plt.show()