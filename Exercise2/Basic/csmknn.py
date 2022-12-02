import sys, os

from features import *
from sklearn.feature_selection import SelectKBest
from tqdm import tqdm


def csm(v1, v2):
    """Cosine similarity between v1 and v2"""
    return ((np.dot(v1,v2)))/(np.linalg.norm(v1,2)*np.linalg.norm(v2,2))

def euc(v1, v2):
    """Euclidean distance between v1 and v2"""
    return np.linalg.norm(v1 - v2,2)

class CSMKNN():
    """Recognizer with K-NN matching, which can use a variable meassure of distance or simmilarity"""

    def __init__(self, k=5, meassure=csm, type="max"):
        """
        Intialze the recognizer:
            k : number of nearest neighbours
            meassure : function that accepts two feature vectors and returns their distance/similarity
            type : 'max' if we use a similarity,
                   'min' if we use a distance
        """
        self.k = k
        self.meassure = meassure
        self.type = type

    def fit(self, X, y):
        # Notes go from 0 to (nClasses - 1)
        # 'Learning' of the recognizer comes from copying the learning dataset
        self.nClasses = y.max() + 1
        self.X = np.copy(X)
        self.y = np.copy(y)

    def predict(self, X):
        """Fuction that calculates notes prediction for samples in matrix X"""
        # Vector where we will save calculated notes from vectors X
        y = np.zeros((X.shape[0],), dtype="int32")

        # Calculate matrix of similarities or distances 
        # between every feature vector in learning dataset and
        # every feature vector in verification dataset
        # self.X is the learning dataset, which we passed in fit() method
        M = np.zeros((X.shape[0], self.X.shape[0]))
        for i in range(X.shape[0]):
            for j in range(self.X.shape[0]):
                M[i, j] = self.meassure(X[i], self.X[j])

        # I-th line of matrix M now includes similarities between
        # the i-th vector in learning dataset and every other vector in learning dataset
        # Function argsort finds the index of K most simmilar vectors
        for i in range(M.shape[0]):
            indeces = np.argsort(M[i])

            # We are interested in most similar vectors 
            # which are at the end of the list for similarities and
            # at the begining of the list for distances
            if self.type == "max":
                neighbours = indeces[-self.k:]
            elif self.type == "min":
                neighbours = indeces[:self.k]
            else:
                raise ValueError("Type must be either 'min' either 'max'")

            # Find note of every nearest neighbour
            notes = [self.y[index] for index in neighbours]

            # Count how many times we find a note of a class in a vector of notes
            noteAppearance = []
            for j in range(self.nClasses):
                noteAppearance_j = np.sum([note == j for note in notes])
                noteAppearance.append(noteAppearance_j)

            # i-temu vektorju v testni zbirki priredimo oznako tistega razreda,
            # ki se med njegovimi K najbližjimi sosedi pojavi največkrat:
            y[i] = np.argmax(noteAppearance)

        return y

def mixLines(X, y):
    """Mixes the matrix of vectors X and notes vector y using the same random permutations"""
    mixedX = np.zeros_like(X)
    mixedY = np.zeros_like(y)

    indeces = np.random.permutation(X.shape[0])

    for i, index in enumerate(indeces):
        mixedX[i] = X[index]
        mixedY[i] = y[index]

    return mixedX, mixedY

def vectorCrossreferencing(X, y, N, picker, recognizer):
    """N-times vector crossreferencing and compare the accuracy of CSMKNN recognizer
       on a dataset, defined by feature vector X and notes vector y
       Parameters:
            @param X: matrix of feature samples
            @param y: vector of sample notes
            @param N: parameter N in N-times crossreferencing/checking
            @param picker: algorithm for picking features which
                           reduces matrix X from (numOfSamples, featureDimensions) to (numOfSamples, smallerDimension)
                           using sklearn.feature_selection.SelectKBest
            @param recognizer: algorith for sorting using matching of nearest neighbours
                           using CSMKNN class"""

    # First we randomly mix matrix X and vector y
    mixedX, mixedY = mixLines(X, y)

    # Dataset is equaly split into N parts
    splitX = []
    splitY = []
    for i in range(N):
        Min = i * round( len(mixedX) / N )
        Max = (i + 1) * round( len(mixedX) / N )
        splitX.append(mixedX[Min:Max,:])
        splitY.append(mixedY[Min:Max])
    
    # List where we save the success rate of sepparate tests
    successRate = []

    # N-times repeated process of learning testing and recognizing 
    # where in i-th part we test on i-th part of the split dataset and learn on all other datasets
    for i in range(N):
        # Matrix of learning samples and their notes - for learning we use all (N-1) parts of the dataset except the i-th one
        X_train = [splitX[ind] for ind in range(N) if ind != i]
        y_train = [splitY[ind] for ind in range(N) if ind != i]

        X_train = np.concatenate(X_train, axis=0)
        y_train = np.concatenate(y_train, axis=0)

        # I-th part of the dataset will be used for testing the learned recognizer
        X_test = splitX[i]
        y_test = splitY[i]

        # Learning picker of features on the learning dataset
        picker.fit(X_train, y_train)

        # Using a random picker on learning and testing features
        X_train = picker.transform(X_train)
        X_test  = picker.transform(X_test)

        # Learning recognizer CSMKNN on learning features
        recognizer.fit(X_train, y_train)

        # Predict notes in recognizer CSMKNN on testing features
        y_hat = recognizer.predict(X_test)

        # Calculate the success of the recognizer on the test dataset
        # Success is meassured as a percentage of predicted notes on the testing dataset
        # which match with the actual notes
        success = np.sum(y_hat == y_test) / len(y_hat)
        successRate.append(success)

    return successRate

def saveFeatures(directory, rootFilename):
    """ Use format <rootFilename><classNumber>__<sample_serial_number>"""
    filenames = os.listdir(directory)
    images = []
    notes = []

    for name in filenames:
        images.append(cv2.imread(directory + name))
        notes.append(int(name.split(rootFilename[-1])[1][0:1]))

    vectors = []
    for image in tqdm(images):
        vector = calculateFastFourierCoeficients(image, 4, 4)
        vectors.append(vector)

    X = np.array(vectors)
    y = np.array(notes)
    np.save("X.npy", X)
    np.save("y.npy", y)
    return (X, y)

def loadFeatures():
    X = np.load("X.npy")
    y = np.load("y.npy")
    return (X, y)