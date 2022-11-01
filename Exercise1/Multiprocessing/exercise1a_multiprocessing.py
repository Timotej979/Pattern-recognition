from tkinter import image_names
from tokenize import Imagnumber
import matplotlib.pyplot as plt
import cv2, sys, logging, time, glob, os
import multiprocessing as mp

from thresholding_multiprocessing import DigitalImageProcessing

def loadImage(filename, grayScaleImagesDict, rgbImagesDict):
    # Read image and convert to correct colourspace
    readImage = cv2.imread(filename)
    readImage = cv2.cvtColor(readImage, cv2.COLOR_BGR2RGB)
    grayScaleImage = cv2.cvtColor(readImage, cv2.COLOR_RGB2GRAY)
    grayScaleImagesDict[filename] = grayScaleImage
    rgbImagesDict[filename] = readImage

def filterImages(usedFilter, grayScaleImage, processedImagesDict):
     # Image processing with 
    #   - histogram equalization
    #   - median Blur
    #   - Gaussian Blur
    if usedFilter == 0:
        processedImagesDict[grayScaleImage[0].rstrip(".jpg") + "-original"] = grayScaleImage[1]
    elif usedFilter == 1:
        processedImagesDict[grayScaleImage[0].rstrip(".jpg") + "-equalizeHist"] = cv2.equalizeHist(grayScaleImage[1])
    elif usedFilter == 2:
        processedImagesDict[grayScaleImage[0].rstrip(".jpg") + "-gaussianBlur"] = cv2.GaussianBlur(grayScaleImage[1], (5, 5), cv2.BORDER_DEFAULT)
    elif usedFilter == 3:
        processedImagesDict[grayScaleImage[0].rstrip(".jpg") + "-medianBlur"] = cv2.medianBlur(grayScaleImage[1], 9)
    else:
        logging.error(" Filtering error, try again")

def objAndPlot(processedImage, rgbImage, grayScaleImage):
    ImageProcessingObj = DigitalImageProcessing(processedImage[1])
    ImageProcessingObj.calculateHistogram()
    ImageProcessingObj.drawHistogram()

    plt.figure()
    plt.title("RGB image " + processedImage[0])
    plt.imshow(rgbImage[1])

    plt.figure()
    plt.title("Grayscale image" + processedImage[0])
    plt.imshow(grayScaleImage[1], cmap = "gray")

    plt.figure()
    plt.title("Processed image" + processedImage[0])
    plt.imshow(processedImage[1], cmap = "gray")

    # Set image threshold
    ImageProcessingObj.setThreshold()
    logging.info("Selected image " + processedImage[0] + " threshold is: {}".format(ImageProcessingObj.imageThreshold))
    _, thresholdedImage = cv2.threshold(processedImage[1], ImageProcessingObj.imageThreshold, 255, 0)

    plt.figure()
    plt.title("Thresholded image" + processedImage[0])
    plt.imshow(thresholdedImage, cmap = "gray")

    plt.show()

def exercise1A_thresholding():

    # Program runtime
    start = time.time()
    startp = time.process_time()

    # Get current directory jpg images
    imageNames = glob.glob("*.jpg")
    
    # Start one multiprocessing context manager and do everything within it
    with mp.Manager() as multimanager:

        # Global mp manager dictionaries to keep track of files
        grayScaleImagesDict = multimanager.dict()
        rgbImagesDict = multimanager.dict()
        processedImagesDict = multimanager.dict()

        # Load images in sepparate processes
        for imageName in imageNames:
            imageLoaderProcess = mp.Process(target = loadImage, args = (imageName, grayScaleImagesDict, rgbImagesDict, ))
            imageLoaderProcess.start()

        imageLoaderProcess.join()

        # Filter images for all possible filters
        for usedFilter in range(0, 3):
            for grayScaleImage in grayScaleImagesDict.items():
                filteringProcess = mp.Process(target = filterImages, args = (usedFilter, grayScaleImage, processedImagesDict, ))
                filteringProcess.start()
    
        filteringProcess.join()

        # Loop through all relevant lists and check if names are matching, in this case execute image analysis
        for processedImage in processedImagesDict.items():
            for rgbImage in rgbImagesDict.items():
                for grayScaleImage in grayScaleImagesDict.items():
                    if processedImage[0].split("-", 1)[0] == rgbImage[0].rstrip(".jpg") and  processedImage[0].split("-", 1)[0] == grayScaleImage[0].rstrip(".jpg"):

                        objAndPlotProcess = mp.Process(target = objAndPlot, args = (processedImage, rgbImage, grayScaleImage, ))
                        objAndPlotProcess.start()

        objAndPlotProcess.join()

    # Program runtime
    # EXECUTION: 36.08s (not exatcly valid/relevant as it is matplotlib window closing dependent)
    # PROCESS: 0.3125s
    stop = time.time()
    stopp = time.process_time()
    logging.info("Program execution time: {} seconds".format(stop - start))
    logging.info("Program process time: {} seconds".format(stopp - startp))

    input("Press any key to exit the program")
    plt.close("all")
    sys.exit(0)

if __name__ == "__main__":
    # Set logging level and start main function
    logging.basicConfig(level = logging.INFO)
    exercise1A_thresholding()