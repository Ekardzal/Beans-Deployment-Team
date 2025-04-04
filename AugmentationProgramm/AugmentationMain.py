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
def augment(_function, _Images, _imageMeta):
    _tempImages = _Images.copy()
    for i in _Images:
        _tempImages.append(doAugmentation(_function, i))
        saveImage(_imageMeta, _tempImages[len(_tempImages) - 1])
    return _tempImages.copy()

def augmentRandom(_function, _limit, _Images, _imageMeta):
    _tempImages = _Images.copy()
    _whitelist = set()
    _rAnzahl = random.randint(_limit[0], _limit[1])
    for x in range(_rAnzahl):
        _rIndex = random.randint(0, len(_Images) - 1)
        while (_rIndex in _whitelist):
            _rIndex = random.randint(0, len(_Images) - 1)
        _whitelist.add(_rIndex)
        _tempImages.append(doAugmentation(_function, _Images[_rIndex]))
        saveImage(_imageMeta, _tempImages[len(_tempImages) - 1])
    return _tempImages.copy()

def doAugmentation(_function, _augmentedImage):
    _augmentor = _function[1](image=_augmentedImage[0])
    _augImage = _augmentor['image']
    return (_augImage, _augmentedImage[1] + _function[0])

def saveImage(_imageMeta, _augmentedImage):
    _outputImagePath = os.path.join(_imageMeta[0], _augmentedImage[1] + '_' + _imageMeta[1])
    _outputTagPath = os.path.join(_imageMeta[0], _augmentedImage[1] + '_' + _imageMeta[2])

    cv2.imwrite(_outputImagePath, _augmentedImage[0])
    _outputTagFile = open(_outputTagPath, "w")
    _outputTagFile.write(_imageMeta[3])
    _outputTagFile.close()

# Main
for imageName in os.listdir(inputDir):
    if imageName.endswith('.jpg') or imageName.endswith('.png'):
        imagePath = os.path.join(inputDir, imageName)
        try:
            tagName = ''
            tagData = ''
            for tagName in os.listdir(inputDir):
                try:
                    if tagName.endswith('.txt'):
                        if os.path.splitext(os.path.basename(tagName))[0] == os.path.splitext(os.path.basename(imageName))[0]:
                            tagPath = os.path.join(inputDir, tagName)
                            tagFile = open(tagPath, 'r')
                            tagData = tagFile.read()
                            tagFile.close()
                            break

                except Exception as e:
                    print(f'Es konnte keine Tag-File gefunden werden.')

            # Basebild einlesen
            imageRaw = Image.open(imagePath).convert('RGB')  # Sicherstellen, dass es RGB ist
            imageData = numpy.array(imageRaw)

            Images = [(imageData, 'AUG_')]
            tempImages = Images.copy()

            imageMeta = (outputDir, imageName, tagName, tagData)

            # Augmentation
            Images = augment(RandomContrast, Images, imageMeta)
            Images = augment(Illumination, Images, imageMeta)
            Images = augment(PlanckianJitter, Images, imageMeta)

            Images = augmentRandom(GaussianBlur, limitBlur, Images, imageMeta)

        except UnidentifiedImageError:
            print(f"Warnung: Das Bild '{imagePath}' konnte nicht geladen werden.")
        #except Exception as e:
        #    print(f"Ein Fehler ist aufgetreten bei '{imagePath}': {e}")