# Dependencies
import os

from PIL import Image, UnidentifiedImageError
import numpy

import albumentations
import cv2

from colorama import Fore, Back, Style

# Variables
inputDir = r'input'
outputDir = r'output'

currentIndex = 0

# region Albumentations
RandomBrightness = ('B', albumentations.RandomBrightnessContrast(
    p=1,
    contrast_limit=0,
    brightness_limit=(-0.2, 0.1)
))
RandomContrast = ('C', albumentations.RandomBrightnessContrast(
    p=1,
    brightness_limit=0
))
Illumination = ('I', albumentations.Illumination(
    p=1
))
PlanckianJitter = ('P', albumentations.PlanckianJitter(
    p=1,
    temperature_limit=(5100, 8500)
))
GaussianBlur = ('g', albumentations.GaussianBlur(
    p=1,
    sigma_limit=(4,8)
))
RGBShift = ('r', albumentations.RGBShift(
    p=1
))
ISONoise = ('N', albumentations.ISONoise(
    p=1
))
#endregion

#region Functions
def augment(function, Images, imageMeta):
    tempImages = Images.copy()
    tempImages.append(doAugmentation(function, tempImages[0]))
    return tempImages.copy()

def doAugmentation(function, augmentedImage):
    augmentor = function[1](image=augmentedImage[0])
    augImage = augmentor['image']
    return (augImage, augmentedImage[1] + function[0])

def saveAll(Images, imageMeta):
    for i in Images:
        outputImagePath = os.path.join(imageMeta[0], i[1] + '_' + imageMeta[1])
        outputTagPath = os.path.join(imageMeta[0], i[1] + '_' + imageMeta[2])

        image = cv2.cvtColor(i[0], cv2.COLOR_RGB2BGR)
        image2 = Image.fromarray(image)
        image2.save(outputImagePath)
        #cv2.imwrite(_outputImagePath, i[0])

        # copy <tag>.txt from Input to Output, if it exists
        if not imageMeta[2] == '':
            outputTagFile = open(outputTagPath, "w")
            outputTagFile.write(imageMeta[3])
            outputTagFile.close()

def initializeBaseImage(imagePath):
    # Convert Image to correct RGB-Array
    imageRaw = Image.open(imagePath).convert('RGB')
    r, g, b = imageRaw.split()
    imageRaw = Image.merge('RGB', (b, g, r))
    imageData = numpy.array(imageRaw)

    # Resize Image
    target_height = 640
    (h, w) = imageData.shape[:2]
    target_scale = target_height / h
    imageData_sized = cv2.resize(imageData, None, fx = target_scale, fy = target_scale)

    return [(imageData_sized, 'AUG_')]

def generateImageMeta(inputDir, outputDir, imageName):
    tagName = ''
    tagData = ''
    for t in os.listdir(inputDir):
        try:
            if t.endswith('.txt'):
                if os.path.splitext(os.path.basename(t))[0] == os.path.splitext(os.path.basename(imageName))[0]:
                    tagName = t
                    tagFile = open(os.path.join(inputDir, tagName), 'r')
                    tagData = tagFile.read()
                    tagFile.close()
                    break

        except Exception as e:
            print(Fore.LIGHTRED_EX + f"Fehler beim einlesen von '{tagName}': {e}")

    return (outputDir, imageName, tagName, tagData)

#endregion

# Main
for imageName in os.listdir(inputDir):
    if imageName.endswith('.jpg') or imageName.endswith('.png'):
        imagePath = os.path.join(inputDir, imageName)
        currentIndex += 1
        try:
            # Initialization
            Images = initializeBaseImage(imagePath)
            imageMeta = generateImageMeta(inputDir, outputDir, imageName)

            # Augmentation
            print(Fore.CYAN + f"[{currentIndex}]" + Style.RESET_ALL + " Augmentiere jetzt '" + imageName + "'...")

            Images = augment(Illumination, Images, imageMeta)  # -> 2
            Images = augment(PlanckianJitter, Images, imageMeta)  # -> 3
            Images = augment(GaussianBlur, Images, imageMeta)  # -> 4

            saveAll(Images, imageMeta)

            print(Fore.GREEN + f"-> erfolgreich gespeichert!")

        except UnidentifiedImageError:
            print(Fore.LIGHTRED_EX + f"Warnung: Das Bild '{imagePath}' konnte nicht geladen werden.")
        except Exception as e:
            print(Fore.LIGHTRED_EX + f"Ein Fehler ist aufgetreten bei '{imagePath}': {e}")