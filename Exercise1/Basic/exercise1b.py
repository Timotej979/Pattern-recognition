import matplotlib.pyplot as plt
import cv2, sys, logging, time

from thresholding import Thresholding
from shapes import Searcher


def exercise1b_shaping():
    # In Short: It allows you to execute code when the file runs as a script, but not when it's imported as a module
    try:
        filename = sys.argv[1]
        usedFilter = sys.argv[2]
    except IndexError:
        logging.error(" Wrong usage of program input arguments\nCorrect program usage: python exercise1.py <Image filename> <Image filter number>\nPossible image filters:\n   0 (original image)\n   1 (equalized histogram)\n   2 (gaussian blur)\n   3 (median blur)\n ")
        sys.exit(1)

    # Program runtime
    start = time.time()
    startp = time.process_time()


    """FIRST EXECUTE EXERCISE1A:"""
    # Read image and convert to correct colourspace
    readImage = cv2.imread(filename)
    readImage = cv2.cvtColor(readImage, cv2.COLOR_BGR2RGB)
    grayScaleImage = cv2.cvtColor(readImage, cv2.COLOR_RGB2GRAY)

    # Image processing with 
    #   - histogram equalization
    #   - median Blur
    #   - Gaussian Blur
    if usedFilter == '0':
        processedImage = grayScaleImage
    elif usedFilter == '1':
        processedImage = cv2.equalizeHist(grayScaleImage)
    elif usedFilter == '2':
        processedImage = cv2.GaussianBlur(grayScaleImage, (5, 5), cv2.BORDER_DEFAULT)
    elif usedFilter == '3':
        processedImage = cv2.medianBlur(grayScaleImage, 9)
    else:
        logging.error(" <Image filter number> not valid, choose numbers 0-3")


    # Create new DIP object to calculate image parameters and display them
    ImageThresholdingObj = Thresholding(processedImage)
    ImageThresholdingObj.calculateHistogram()
    ImageThresholdingObj.drawHistogram()

    plt.figure()
    plt.title("RGB image")
    plt.imshow(readImage)

    plt.figure()
    plt.title("Grayscale image")
    plt.imshow(grayScaleImage, cmap = "gray")

    plt.figure()
    plt.title("Processed image")
    plt.imshow(processedImage, cmap = "gray")

    # Set image threshold
    ImageThresholdingObj.setThreshold()
    logging.info("Selected image threshold is: {}".format(ImageThresholdingObj.imageThreshold))
    _, thresholdedImage = cv2.threshold(processedImage, ImageThresholdingObj.imageThreshold, 255, 0)

    plt.figure()
    plt.title("Thresholded image")
    plt.imshow(thresholdedImage, cmap = "gray")


    """SECOND EXECUTE EXERCISE1B:"""
    ImageSearcherObj = Searcher(thresholdedImage)
    ImageSearcherObj.searchShapes()

    print(ImageSearcherObj.shapes)


    # TODO: write code in Searcher class
    # TODO: find shapes in thresholded image
    # TODO: separately draw all shapes and one shape at a time
    # TODO: save longest shape in text file in points list

    plt.show(block=False)

    input("Press any key.")
    plt.close("all")
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    exercise1b_shaping()