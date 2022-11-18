import matplotlib.pyplot as plt
import cv2, sys, logging, time, os

from sklearn.feature_selection import SelectKBest
from features import *


def exercise1c_features():
    # Read all images from Pictures/ directory preprocess them and save them to a list
    directory = 'Pictures/'
    try:
        inputImages = next(os.walk(directory), (None, None, []))[2]
    except:
        logging.error("Error reading directory /Pictures/")

    # Calculate feature vector for every picture
    vectorsFFC = []
    for inputImage in inputImages:
        vectorFFC = calculateFastFourierCoeficients( cv2.imread(directory + inputImage), 4, 4 )
        vectorsFFC.append(vectorFFC)

    # Plot feature vectors
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
    plt.show()

    # Pick the best features for spliting appart different object classes
    X = np.array(vectorsFFC)
    y = np.array([0, 0, 0, 1, 1, 1])
    X_new = SelectKBest(k=4).fit_transform(X, y)

    # Show feature vectors with cosine similarity and euclidean distance
    distancesEVK = np.zeros((6, 6), dtype="float64")
    cosineSimmilarities = np.zeros_like(distancesEVK)

    for i in range(len(vectorsFFC)):
        for j in range(len(vectorsFFC)):
            v1 = X_new[i]
            v2 = X_new[j]

            # Calculate cosine similarity and negative euclidean distance between vectors v1 and v2
            distancesEVK[i, j] = -np.linalg.norm(v1 - v2,2)
            cosineSimmilarities[i, j] = ((np.dot(v1,v2)))/(np.linalg.norm(v1,2)*np.linalg.norm(v2,2))

    plt.figure()
    plt.title("Negative Euclidian distance")
    plt.imshow(distancesEVK)
    plt.colorbar()
    plt.tight_layout()
    plt.show()

    plt.figure()
    plt.title("Cosine simmilarity")
    plt.imshow(cosineSimmilarities)
    plt.colorbar()
    plt.tight_layout()
    plt.show()
    

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    exercise1c_features()