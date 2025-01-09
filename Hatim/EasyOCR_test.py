from time import sleep

import easyocr
import time
from PIL import Image, ImageDraw

def askEasyOCR(path):
    #Reader initialisieren
    reader = easyocr.Reader(['en'])
    path = path

    print("======== EasyOCR-Prozess gestartet ========")

    #Start Timer
    start = time.time()

    #Lies Text von Bild
    result = reader.readtext(path)


    #Stop Timer
    end = time.time()
    duration = (end - start) * 10**3


    '''
    print()
    print(result)
    '''

    #Initialisierung Liste
    bbox = []
    image = Image.open(path)
    draw = ImageDraw.Draw(image)

    #Initialisierung Rückgabeparameter
    words = []
    positions = []
    probs = []

    #gehe durch Liste, trenne Ergebnisse jeweils in bbox, Text und probability
    for res in result:

        positions.append(res[0])
        words.append(res[1])
        probs.append(res[2])


        bbox = res[0]
        text = res[1]
        prob = res[2]
    
        '''
        print(f"Text: {text}")
        print(f"Koordinaten: {bbox}")
        print(f"Sicherheit: {prob*100:0.04f}%")
        print("----------------------")
        '''

        #Rechteck einzeichnen
        xy = [(bbox[0][0],bbox[0][1]),(bbox[2][0],bbox[2][1])]
        #draw.rectangle(xy, width=1, outline = "red")



    #print(f"Der Prozess hat {duration:.03f}ms gedauert")

    #image.show()

    return words, positions, probs, image, duration


