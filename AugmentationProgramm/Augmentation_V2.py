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

imageName = ''

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
def augment(_function, _Images, _imageMeta):
    _tempImages = _Images.copy()
    _tempImages.append(doAugmentation(_function, _tempImages[0]))
    return _tempImages.copy()

def doAugmentation(_function, _augmentedImage):
    _augmentor = _function[1](image=_augmentedImage[0])
    _augImage = _augmentor['image']
    return (_augImage, _augmentedImage[1] + _function[0])

def saveAll(_Images, _imageMeta):
    for i in _Images:
        _outputImagePath = os.path.join(_imageMeta[0], i[1] + '_' + _imageMeta[1])
        _outputTagPath = os.path.join(_imageMeta[0], i[1] + '_' + _imageMeta[2])

        cv2.imwrite(_outputImagePath, i[0])

        # copy <tag>.txt from Input to Output, if it exists
        if not _imageMeta[2] == '':
            _outputTagFile = open(_outputTagPath, "w")
            _outputTagFile.write(_imageMeta[3])
            _outputTagFile.close()

def initializeBaseImage(_imagePath):
    # Convert Image to correct RGB-Array
    _imageRaw = Image.open(_imagePath).convert('RGB')
    r, g, b = _imageRaw.split()
    _imageRaw = Image.merge('RGB', (b, g, r))
    _imageData = numpy.array(_imageRaw)

    return [(_imageData, 'AUG_')]

def generateImageMeta(_inputDir, _outputDir, _imageName):
    _tagName = ''
    _tagData = ''
    for _tagName in os.listdir(_inputDir):
        try:
            if _tagName.endswith('.txt'):
                if os.path.splitext(os.path.basename(_tagName))[0] == os.path.splitext(os.path.basename(_imageName))[0]:
                    _tagFile = open(os.path.join(_inputDir, _tagName), 'r')
                    _tagData = _tagFile.read()
                    _tagFile.close()
                    break

        except Exception as e:
            print(Fore.LIGHTRED_EX + f"Fehler beim einlesen von '{_tagName}': {e}")

    return (_outputDir, _imageName, _tagName, _tagData)
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