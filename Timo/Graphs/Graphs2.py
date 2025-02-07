import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt
import csv

#------------------------------------------------------------------------------------------------------------#
#Weiteres "Stacked" Histogramm mit mehreren Ergebnissen in einem file
# con_xxep = Liste mit Listen (1. Liste = Ergebnis Dose, 2. Liste = Ergebnis Label)
con_20ep = [[], []]
with open("predres/20e/sorted_results.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            if row[2] == "Dose1":
                con_20ep[0].append(float(row[1]))
            elif row[2] == "Label":
                con_20ep[1].append(float(row[1]))
        except ValueError:
            continue

con_40ep = [[], []]
with open("predres/40e/sorted_results.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            if row[2] == "Dose1":
                con_40ep[0].append(float(row[1]))
            elif row[2] == "Label":
                con_40ep[1].append(float(row[1]))
        except ValueError:
            continue

con_60ep = [[], []]
with open("predres/60e/sorted_results.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            if row[2] == "Dose1":
                con_60ep[0].append(float(row[1]))
            elif row[2] == "Label":
                con_60ep[1].append(float(row[1]))
        except ValueError:
            continue

con_80ep = [[], []]
with open("predres/80e/sorted_results.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            if row[2] == "Dose1":
                con_80ep[0].append(float(row[1]))
            elif row[2] == "Label":
                con_80ep[1].append(float(row[1]))
        except ValueError:
            continue

avg_con20epD = np.average(con_20ep[0])
avg_con20epL = np.average(con_20ep[1])
avg_con20ep = np.average([avg_con20epD, avg_con20epL])
avg_con40epD = np.average(con_40ep[0])
avg_con40epL = np.average(con_40ep[1])
avg_con40ep = np.average([avg_con40epD, avg_con40epL])
avg_con60epD = np.average(con_60ep[0])
avg_con60epL = np.average(con_60ep[1])
avg_con60ep = np.average([avg_con60epD, avg_con60epL])
avg_con80epD = np.average(con_80ep[0])
avg_con80epL = np.average(con_80ep[1])
avg_con80ep = np.average([avg_con80epD, avg_con80epL])
#Liniendiagramm mit dem avg der Ergebnisse von den Epochenabschnitten, unterteilt in Avg, Avg Dose, Avg Label
fig, ax = plt.subplots()
ax.plot(("20 Epochen", "40 Epochen", "60 Epochen", "80 Epochen"), (avg_con20ep, avg_con40ep, avg_con60ep, avg_con80ep), "bo", linestyle="-",  color="tab:orange", label="Durchschnitt")
ax.plot((avg_con20epD, avg_con40epD, avg_con60epD, avg_con80epD), "bo", linestyle="-", color="#042aff", label="Durchschnitt Dosen")
ax.plot((avg_con20epL, avg_con40epL, avg_con60epL, avg_con80epL), "bo", linestyle="-", color="#0bdbeb", label="Durchschnitt Labels")
ax.set_ylim(0.65, 0.95)
ax.set_yticks(np.arange(0.65, 0.95, 0.03))
ax.set_ylabel("Confidence")
ax.set_title("Durchschnittliche Confidence pro Trainingsabschnitt")
fig.set_size_inches(7, 5)
ax.legend()
plt.show()

del fig, ax
#------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------------------------#
# Histogramme zu den Trainingsabschnitten der Klassen Dose, Label
fig, (ax, bx) = plt.subplots(1, 2, sharex=True)
ax.hist(con_20ep[0], label="20 Epochen", color="#004e9e")
ax.hist(con_40ep[0], alpha=0.9, label="40 Epochen", color="tab:orange")
ax.hist(con_80ep[0], label="80 Epochen", color="tab:green", alpha=0.8)
bx.hist(con_20ep[1], label="20 Epochen", color="#004e9e")
bx.hist(con_40ep[1], alpha=0.9, label="40 Epochen", color="tab:orange")
bx.hist(con_80ep[1], label="80 Epochen", color="tab:green", alpha=0.8)
ax.set_ylabel("Anzahl Bilder")
ax.set_xlabel("Confidence")
bx.set_ylabel("Anzahl Bilder")
bx.set_xlabel("Confidence")
ax.set_title("Histogramme Confidences Dosen")
bx.set_title("Histogramme Confidences Labels")
fig.suptitle("Histogramme verschiedener Trainingsabschnitte")
fig.set_size_inches(9, 6)
ax.legend()
bx.legend()
plt.show()

del fig, ax, bx
#------------------------------------------------------------------------------------------------------------#
#Aufteilen der Histogramme (besser für Farbenblinde)
fig, (ax, bx) = plt.subplots(1, 2, sharex=True)
ax.hist(con_20ep[0], label="20 Epochen", color="#004e9e")

bx.hist(con_80ep[0], label="80 Epochen", color="tab:green")

ax.set_ylabel("Anzahl Bilder")
ax.set_xlabel("Confidence")
bx.set_ylabel("Anzahl Bilder")
bx.set_xlabel("Confidence")

ax.set_title("Histogramm Confidences Dosen 20 Epochen")
bx.set_title("Histogramm Confidences Dosen 80 Epochen")
fig.suptitle("Histogramm verschiedener Trainingsabschnitte")
fig.set_size_inches(9, 6)

plt.show()
del fig, ax, bx

fig, (ax, bx) = plt.subplots(1, 2, sharex=True)



ax.hist(con_20ep[1], label="20 Epochen", color="#004e9e")

bx.hist(con_80ep[1], label="80 Epochen", color="tab:green")
ax.set_ylabel("Anzahl Bilder")
ax.set_xlabel("Confidence")
bx.set_ylabel("Anzahl Bilder")
bx.set_xlabel("Confidence")
ax.set_title("Histogramm Confidences Labels 20 Epochen")
bx.set_title("Histogramm Confidences Labels 80 Epochen")
fig.suptitle("Histogramm verschiedener Trainingsabschnitte")
fig.set_size_inches(9, 6)
plt.show()