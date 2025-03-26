# Dependencies
import os
from PIL import Image, UnidentifiedImageError
import numpy

import albumentations
import cv2

# Variables
inputDir = r"D:\_HSMW_Stuff\WW\WW_2\AugmentationProgramm\input"
outputDir = r"D:\_HSMW_Stuff\WW\WW_2\AugmentationProgramm\output"

# Annotation class
class augmentableImage:
    def __init__(self, imageName, imageData):
        self.imageName = imageName
        self.imageData = imageData

# Augmentations
augmentIllumination = albumentations.Illumination(

)

# Main
for imageName in os.listdir(inputDir):
    if imageName.endswith(".jpg") or imageName.endswith(".png"):
        imagePath = os.path.join(inputDir, imageName)
        try:
            imageRaw = Image.open(imagePath).convert("RGB")  # Sicherstellen, dass es RGB ist
            imageData = numpy.array(imageRaw)

            #augImage = augmentableImage(imageName, imageData)
            augmentor = augmentIllumination(image=imageData)
            augmentedImage = augmentor['image']

            outputImagePath = os.path.join(outputDir, 'aug'+imageName)
            cv2.imwrite(outputImagePath, augmentedImage)

        except UnidentifiedImageError:
            print(f"Warnung: Das Bild '{imagePath}' konnte nicht geladen werden.")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten bei '{imagePath}': {e}")

#test1 = augmentableImage("red", 3812.4)