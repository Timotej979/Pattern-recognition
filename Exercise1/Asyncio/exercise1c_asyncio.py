import matplotlib.pyplot as plt
import cv2, os, logging, asyncio, aiofiles, functools, time
from concurrent.futures import ProcessPoolExecutor

from sklearn.feature_selection import SelectKBest
from features_asyncio import *


"""SUPPORT FUNCTION"""
def listDirFiles(directory):
    """Read all images from Pictures/ directory preprocess them and save them to a list"""
    try:
        inputImages = next(os.walk(directory), (None, None, []))[2]
        return inputImages
    except:
        logging.error("Error reading directory /Pictures/")


"""MAIN ASYNC FUNCTION"""
async def exercise1c_features():
    # Program runtime
    start = time.time()
    startp = time.process_time()

    # Change directory folder of images here
    directory = 'Pictures/'
    inputImages = await loop.run_in_executor(executor, functools.partial(listDirFiles, directory))

    # Calculate feature vector for every picture
    vectorsFFC = []
    for inputImage in inputImages:
        vectorFFC = await calculateFastFourierCoeficients( cv2.imread(directory + inputImage), 4, 4 )
        vectorsFFC.append(vectorFFC)

    # Calculate feature vectors
    logX = []
    logShow = []
    logColor = []
    for i in range(len(vectorsFFC)):
        if i < 3:
            color = "b"
        else:
            color = "g"
        
        modifiedVector = vectorsFFC[i]
        x = np.arange(len(modifiedVector)) + 0.12 * i 

        # For better display of values we used the logarithmic scale by using the equation:
        # logShow = sign(vector) * log_10( |vector| )
        logShow = np.sign(modifiedVector) * np.log10(np.abs(modifiedVector))
        plt.bar(x, logShow, width=0.1, color=color)

    plt.grid(True)

    # Pick the best features for spliting appart different object classes
    X = np.array(vectorsFFC)
    y = np.array([0, 0, 0, 1, 1, 1])
    X_new = SelectKBest(k=4).fit_transform(X, y)

    # Show feature vectors with cosine similarity and euclidean distance
    distancesEVK = np.zeros((6, 6), dtype="float64")
    cosineSimilarities = np.zeros_like(distancesEVK)

    for i in range(len(vectorsFFC)):
        for j in range(len(vectorsFFC)):
            v1 = X_new[i]
            v2 = X_new[j]

            # Calculate cosine similarity and negative euclidean distance between vectors v1 and v2
            distancesEVK[i, j] = -np.linalg.norm(v1 - v2,2)
            cosineSimilarities[i, j] = ((np.dot(v1,v2)))/(np.linalg.norm(v1,2)*np.linalg.norm(v2,2))

    plt.figure()
    plt.title("Negative Euclidian distance")
    plt.imshow(distancesEVK)
    plt.colorbar()
    plt.tight_layout()

    plt.figure()
    plt.title("Cosine similarity")
    plt.imshow(cosineSimilarities)
    plt.colorbar()
    plt.tight_layout()
    plt.show()

    # Program execution time
    stop = time.time()
    stopp = time.process_time()

    # Program runtime
    logging.info("Program execution time: {} seconds".format(stop - start))
    logging.info("Program process time: {} seconds".format(stopp - startp))


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    executor = ProcessPoolExecutor(1)

    # Get asyncio loop and start function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(exercise1c_features())
    