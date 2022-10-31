from concurrent.futures import process
from cv2 import BORDER_DEFAULT
import matplotlib.pyplot as plt
import cv2, sys

from thresholding import DigitalImageProcessing


def exercise1A_thresholding():
    # In Short: It allows you to execute code when the file runs as a script, but not when it's imported as a module
    try:
        filename = sys.argv[1]
        usedFilter = sys.argv[2]
    except IndexError:
        print("Program usage: python exercise1.py <Image filename> <Image filter>")
        print("Possible image filters:\n   0 (original image)\n   1 (equalized histogram)\n   2 (gaussian blur)\n   3 (median blur)\n ")
        sys.exit(1)

    # Read image and convert to correct colourspace
    readImage = cv2.imread(filename)
    readImage = cv2.cvtColor(readImage, cv2.COLOR_BGR2RGB)
    grayScaleImage = cv2.cvtColor(readImage, cv2.COLOR_RGB2GRAY)

    # Image processing with 
    #   - histogram equalization
    #   - median Blur
    #   - Gaussian Blur
    match usedFilter:
        case 0:
            processedImage = grayScaleImage
        case 1:
            processedImage = cv2.equalizeHist(grayScaleImage)
        case 2:
            processedImage = cv2.GaussianBlur(grayScaleImage, (5, 5), BORDER_DEFAULT)
        case 3:
            processedImage = cv2.medianBlur(grayScaleImage, 9)

    ImageProcessingObj = DigitalImageProcessing(processedImage)
    print(ImageProcessingObj.grayScaleImage)




if __name__ == "__main__":
    exercise1A_thresholding()