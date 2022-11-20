import matplotlib.pyplot as plt
import cv2, logging, time, os
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

def calculateEuclideanCosine(j, k, X_new, mpDistancesEVKArray, mpCosineSimilaritiesArray, mpLock):
    # Set vectors v1 and v2
    v1 = X_new[j]
    v2 = X_new[k]

    # Synchronize array access using acquire multiprocessing Lock() 
    with mpLock:
         # Get array from shared memory
        distancesEVKArray = np.frombuffer(mpDistancesEVKArray.get_obj()).reshape((6, 6))
        # Get array from shared memory
        cosineSimilaritiesArray = np.frombuffer(mpCosineSimilaritiesArray.get_obj()).reshape((6, 6))
        # Calculate negative euclidean distance between vectors v1 and v2
        distancesEVKArray[j, k] = -np.linalg.norm(v1 - v2,2)
        # Calculate cosine similarity between vectors v1 and v2
        cosineSimilaritiesArray[j, k] = ((np.dot(v1,v2)))/(np.linalg.norm(v1,2)*np.linalg.norm(v2,2))
        # Release multiprocesing Lock()

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

        # Shared memory 2D numpy array
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

        # Create multiprocessing lock object and limit the number of processes runing simuntaneously 
        # Limit is set to 3 because we have 3 hammer images and 3 wrench images,
        # therefore when we calculate distances between eachother the 3x3 calculations are roughly the same in time complexity (Prevents race condition)
        mpLock = mp.Lock()
        processesList = []
        maxNumOfProcesses = 3

        # Calculate euclidean distance and cosine similarity
        for j in range(len(vectorsFFCList)):
            for k in range(len(vectorsFFCList)):
                # Maximum num of processes set, after reach we join them
                if(len(processesList) <= maxNumOfProcesses):
                    calculateEuclideanCosineProcess = mp.Process(target = calculateEuclideanCosine, args = (j, k, X_new, mpDistancesEVKArray, mpCosineSimilaritiesArray, mpLock, ))
                    calculateEuclideanCosineProcess.start()
                    processesList.append(calculateEuclideanCosineProcess)
                else:
                    for process in processesList:
                        process.join()
                    # After the join of 6 processes, clear processesList and continue
                    processesList.clear()
                    calculateEuclideanCosineProcess = mp.Process(target = calculateEuclideanCosine, args = (j, k, X_new, mpDistancesEVKArray, mpCosineSimilaritiesArray, mpLock, ))
                    calculateEuclideanCosineProcess.start()
                    processesList.append(calculateEuclideanCosineProcess)
                    
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