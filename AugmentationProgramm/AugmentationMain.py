# Dependencies
import os
import random

from PIL import Image, UnidentifiedImageError
import numpy

import albumentations
import cv2

# Directories
inputDir = r'input'
outputDir = r'output'

# Albumentations
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
    p=1
))
GaussianBlur = ('g', albumentations.GaussianBlur(
    p=1,
    sigma_limit=(4,8)
))

# Quantity Limits
limitBlur = (2, 5)

# Functions
def augment(_function, _Images, _outputDir, _imageName):
    _tempImages = _Images.copy()
    for i in _Images:
        _tempImages.append(doAugmentation(_function, i[0], i[1]))
        saveImage(_outputDir, _tempImages[len(_tempImages) - 1], _imageName)
    return _tempImages.copy()

def augmentRandom(_function, _limit, _Images, _outputDir, _imageName):
    _tempImages = _Images.copy()
    _whitelist = set()
    _rAnzahl = random.randint(_limit[0], _limit[1])
    for x in range(_rAnzahl):
        _rIndex = random.randint(0, len(_Images) - 1)
        while (_rIndex in _whitelist):
            _rIndex = random.randint(0, len(_Images) - 1)
        _whitelist.add(_rIndex)
        _tempImages.append(doAugmentation(_function, _Images[_rIndex][0], _Images[_rIndex][1]))
        saveImage(_outputDir, _tempImages[len(_tempImages) - 1], _imageName)
    return _tempImages.copy()

def doAugmentation(_function, _imageData, _imageAppendix):
    _augmentor = _function[1](image=_imageData)
    _augImage = _augmentor['image']
    return (_augImage, _imageAppendix + _function[0])

def saveImage(_outputDir, _augmentedImage, _imageName):
    _outputImagePath = os.path.join(_outputDir, _augmentedImage[1] + '_' + _imageName)
    cv2.imwrite(_outputImagePath, _augmentedImage[0])

# Main
for imageName in os.listdir(inputDir):
    if imageName.endswith('.jpg') or imageName.endswith('.png'):
        imagePath = os.path.join(inputDir, imageName)
        try:
            # Basebild einlesen
            imageRaw = Image.open(imagePath).convert('RGB')  # Sicherstellen, dass es RGB ist
            imageData = numpy.array(imageRaw)

            Images = [(imageData, 'AUG_')]
            tempImages = [(imageData, 'AUG_')]

            # Augmentation
            Images = augment(RandomContrast, Images, outputDir, imageName)
            Images = augment(Illumination, Images, outputDir, imageName)
            Images = augment(PlanckianJitter, Images, outputDir, imageName)

            Images = augmentRandom(GaussianBlur, limitBlur, Images, outputDir, imageName)

        except UnidentifiedImageError:
            print(f"Warnung: Das Bild '{imagePath}' konnte nicht geladen werden.")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten bei '{imagePath}': {e}")