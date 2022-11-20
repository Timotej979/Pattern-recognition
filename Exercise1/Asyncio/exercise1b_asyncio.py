import matplotlib.pyplot as plt
import cv2, sys, logging, asyncio, aiofiles, functools, time
from concurrent.futures import ProcessPoolExecutor

from thresholding_asyncio import Thresholding
from shapes_asyncio import Searcher


"""SUPPORT FUNCTIONS:"""
def loadImage(filename):
    readImage = cv2.imread(filename)
    readImage = cv2.cvtColor(readImage, cv2.COLOR_BGR2RGB)
    grayScaleImage = cv2.cvtColor(readImage, cv2.COLOR_RGB2GRAY)
    return readImage, grayScaleImage

def filterImage(usedFilter, grayScaleImage):
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
    return processedImage

def thresholdImage(processedImage, ImageProcessingObj):
    # Set image threshold
    logging.info("Selected image threshold is: {}".format(ImageProcessingObj.imageThreshold))
    _, thresholdedImage = cv2.threshold(processedImage, ImageProcessingObj.imageThreshold, 255, 0)
    return thresholdedImage

def displayPlots(readImage, grayScaleImage, processedImage, thresholdedImage, ImageProcessingObj, allShapesImage, longestShapeImage):
    # Display simple plots
    ImageProcessingObj.drawHistogram()

    plt.figure()
    plt.title("RGB image")
    plt.imshow(readImage)

    plt.figure()
    plt.title("Grayscale image")
    plt.imshow(grayScaleImage, cmap = "gray")

    plt.figure()
    plt.title("Processed image")
    plt.imshow(processedImage, cmap = "gray")

    plt.figure()
    plt.title("Thresholded image")
    plt.imshow(thresholdedImage, cmap = "gray")

    plt.figure()
    plt.title("Image with all shapes")
    plt.imshow(allShapesImage, cmap = 'gray')

    plt.figure()
    plt.title("Image with the longest shape")
    plt.imshow(longestShapeImage, cmap = 'gray')

    # Program runtime
    stop = time.time()
    stopp = time.process_time()
    plt.show()
    return stop, stopp


"""MAIN ASYNC FUNCTION:"""
async def exercise1b_shaping(filename, usedFilter):
    # Program runtime
    start = time.time()
    startp = time.process_time()
    
    """FIRST EXECUTE EXERCISE1A:"""
    # Read image and convert to correct colourspace
    readImage, grayScaleImage = await loop.run_in_executor(executor, functools.partial(loadImage, filename))
    
    # Process image
    processedImage = await loop.run_in_executor(executor, functools.partial(filterImage, usedFilter, grayScaleImage))

    # Create new Thresholding object to calculate image parameters and display them
    ImageProcessingObj = Thresholding(processedImage)

    # Await all tasks while displaying simple plots
    await ImageProcessingObj.calculateHistogram()
    await ImageProcessingObj.setThreshold()

    thresholdedImage = await loop.run_in_executor(executor, functools.partial(thresholdImage, processedImage, ImageProcessingObj))

    """SECOND EXECUTE EXERCISE1B:"""
    ImageSearcherObj = Searcher(thresholdedImage)
    await ImageSearcherObj.searchShapes()

    allShapesImage = await ImageSearcherObj.drawAllShapes([80, 255])

    longestShape = await ImageSearcherObj.getLongestShape()
    longestShapeImage = await ImageSearcherObj.drawShape(longestShape, 255)

    async with aiofiles.open('LongestShape.txt', 'w') as f:
        await f.write(str(longestShape.get('points')))

    stop, stopp = await loop.run_in_executor(executor, functools.partial(displayPlots, readImage,grayScaleImage, processedImage, thresholdedImage, ImageProcessingObj, allShapesImage, longestShapeImage))

    # Program runtime
    logging.info("Program execution time: {} seconds".format(stop - start))
    logging.info("Program process time: {} seconds".format(stopp - startp))

    input("Press any key to exit the program")
    plt.close("all")
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    executor = ProcessPoolExecutor(1)

    # In Short: It allows you to execute code when the file runs as a script, but not when it's imported as a module
    try:
        filename = sys.argv[1]
        usedFilter = sys.argv[2]
    except IndexError:
        logging.error(" Wrong usage of program input arguments\nCorrect program usage: python exercise1.py <Image filename> <Image filter number>\nPossible image filters:\n   0 (original image)\n   1 (equalized histogram)\n   2 (gaussian blur)\n   3 (median blur)\n ")
        sys.exit(1)

    # Get asyncio loop and start function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(exercise1b_shaping(filename, usedFilter))