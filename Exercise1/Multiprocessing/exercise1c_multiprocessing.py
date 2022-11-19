import matplotlib.pyplot as plt
import cv2, sys, logging, time, os, ctypes
import multiprocessing as mp

from sklearn.feature_selection import SelectKBest
from features_multiprocessing import *


"""SUPPORT FUNCTIONS"""
def calculateVectorsFFCList(directory, inputImage, vectorsFFCList):
    # Calculate feature vector for every picture
    vectorFFC = calculateFastFourierCoeficients( cv2.imread(directory + inputImage), 4, 4 )
    vectorsFFCList.append(vectorFFC)

def plotVectorsFFC(i, vectorsFFCList, inputImages):
    # Plot feature vectors
    if i < 3:
        color = "b"
    else:
        color = "g"
    
    modifiedVector = vectorsFFCList[i]
    x = np.arange(len(modifiedVector)) + 0.12 * i

    # For better display of values we used the logarithmic scale by using the equation:
    # logShow = sign(vector) * log_10( |vector| )
    logShow = np.sign(modifiedVector) * np.log10(np.abs(modifiedVector))
    plt.bar(x, logShow, width=0.1, color=color)
    plt.title("FFC " + inputImages[i])
    plt.grid(True)
    plt.show()

def calculateEuclideanCosine(j, k, X_new, mpDistancesEVKArray, mpCosineSimilaritiesArray):
    # Synchronize array access
    with mpDistancesEVKArray.get_lock():
        with mpCosineSimilaritiesArray.get_lock():
            # Get arrays from shared memory
            distancesEVKArray = np.frombuffer(mpDistancesEVKArray.get_obj()).reshape((6, 6))
            cosineSimilaritiesArray = np.frombuffer(mpCosineSimilaritiesArray.get_obj()).reshape((6, 6))

            # Set vectors v1 and v2
            v1 = X_new[j]
            v2 = X_new[k]

            # Calculate cosine similarity and negative euclidean distance between vectors v1 and v2
            distancesEVKArray[j, k] = -np.linalg.norm(v1 - v2,2)
            cosineSimilaritiesArray[j, k] = ((np.dot(v1,v2)))/(np.linalg.norm(v1,2)*np.linalg.norm(v2,2))

def plotEuclideanCosine(mpDistancesEVKArray, mpCosineSimilaritiesArray):
    plt.figure()
    plt.title("Negative Euclidian distance")
    plt.imshow(np.frombuffer(mpDistancesEVKArray.get_obj()).reshape((6, 6)))
    plt.colorbar()
    plt.tight_layout()
    
    plt.figure()
    plt.title("Cosine similarity")
    plt.imshow(np.frombuffer(mpCosineSimilaritiesArray.get_obj()).reshape((6, 6)))
    plt.colorbar()
    plt.tight_layout()
    plt.show()


"""MAIN FUNCTION"""
def exercise1c_features():
    # Program runtime
    start = time.time()
    startp = time.process_time()

    # Read all images from Pictures/ directory preprocess them and save them to a list
    directory = 'Pictures/'
    try:
        inputImages = next(os.walk(directory), (None, None, []))[2]
    except:
        logging.error("Error reading directory /Pictures/")

    with mp.Manager() as multimanager:

        # Global mp manager dictionaries to keep track of files
        vectorsFFCList = multimanager.list()

        # Shared memory 2D numpy array with reference to use in function
        mpDistancesEVKArray = mp.Array('d', 6*6)

        mpCosineSimilaritiesArray = mp.Array('d',6*6)

        # Calculate feature vector for every picture
        for inputImage in inputImages:
            calculateFFCListProcess = mp.Process(target = calculateVectorsFFCList, args = (directory, inputImage, vectorsFFCList, ))
            calculateFFCListProcess.start()
            
        calculateFFCListProcess.join()

    	# Pick the best features for spliting appart different object classes
        X = np.array(vectorsFFCList)
        y = np.array([0, 0, 0, 1, 1, 1])
        X_new = SelectKBest(k=4).fit_transform(X, y)

        # Calculate euclidean distance and cosine similarity
        for j in range(len(vectorsFFCList)):
            for k in range(len(vectorsFFCList)):
                calculateEuclideanCosineProcess = mp.Process(target = calculateEuclideanCosine, args = (j, k, X_new, mpDistancesEVKArray, mpCosineSimilaritiesArray, ))
                calculateEuclideanCosineProcess.start()

        calculateEuclideanCosineProcess.join()

        # Plot feature vector for every picture on a sepparate graph
        for i in range(len(vectorsFFCList)):
            plotVectorsFFCProcess = mp.Process(target = plotVectorsFFC, args = (i, vectorsFFCList, inputImages, ))
            plotVectorsFFCProcess.start()

        plotVectorsFFCProcess.join()

        # Plot euclidean distances and cosine similarities
        plotEuclideanCosineProcess = mp.Process(target = plotEuclideanCosine, args = (mpDistancesEVKArray, mpCosineSimilaritiesArray, ))
        plotEuclideanCosineProcess.start()
        plotEuclideanCosineProcess.join()

    # Program runtime
    stop = time.time()
    stopp = time.process_time()
    logging.info("Program execution time: {} seconds".format(stop - start))
    logging.info("Program process time: {} seconds".format(stopp - startp))
    

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    exercise1c_features()