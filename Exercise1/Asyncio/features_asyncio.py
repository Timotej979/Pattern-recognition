from shapes_asyncio import *
import cv2
from thresholding_asyncio import *


async def preprocessImage(inputImage):
    """Side function to pre-process the input image."""

    # Convert picture to grayscale
    processedImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)

    # Oversample image with resizing to 256x256 pixels
    processedImage = cv2.resize(processedImage, dsize = (256, 256), interpolation = cv2.INTER_CUBIC)

    # Apply a median blur of 11 neighbours
    processedImage = cv2.medianBlur(processedImage, 11)

    # Threshold the medianBluredImage
    ImageThresholdingObj = Thresholding(processedImage)
    await ImageThresholdingObj.calculateHistogram()
    await ImageThresholdingObj.setThreshold()
    _, thresholdedImage = cv2.threshold(processedImage, ImageThresholdingObj.imageThreshold, 255, 0)

    return thresholdedImage

async def shape2Signal(shape):
    """Convert shapePoints sequence to the complex signal"""
    shapePoints = shape["points"]
    shapeLength = len(shapePoints)
    shapeSignal = np.zeros((shapeLength,), dtype=np.complex128)
    
    # For loop over shapePoints and project them onto the complex plane
    shapeSignal = np.array( [ ( (shapePoints[i][0]) + (shapePoints[i][1])*1j ) for i in range(shapeLength) ], dtype=np.complex128 )

    return shapeSignal

async def oversampleSignal(signal, newN = 64):
    """Oversample a signal of variable length to a fixed degree of points"""
    N_orig = signal.shape[0]
    newSignal = np.zeros((newN,), dtype=signal.dtype)
    for i in range(newN):
        i_r = i / (newN - 1)
        j_r = i_r * (N_orig - 1)

        if j_r == 0 or j_r == (N_orig - 1):
            newSignal[i] = signal[int(j_r)]
        else:
            j0 = int(j_r)
            j1 = j0 + 1
            t = j_r - j0

            y0 = signal[j0]
            y1 = signal[j1]
            newSignal[i] = y0 * (1 - t) + y1 * t

    return newSignal

async def calculateFastFourierCoeficients(inputImage, kmax, lmax):
    """Calculate a vector of features from the longest shape on the picture"""
    binaryImage = await preprocessImage(inputImage)

    shapeSearcher = Searcher(binaryImage)
    await shapeSearcher.searchShapes()
    longestShape = await shapeSearcher.getLongestShape()

    signal = await shape2Signal(longestShape)
    signal = await oversampleSignal(signal)

    signalFastFourierTransform = np.fft.fft(signal)

    vectorFastFourierCoeficients = np.zeros((2 * kmax * (lmax - 1),), dtype=np.float64)
    indexVector = 0

    for i in range(1, kmax + 1):
        for j in range(2, lmax + 1):
            F_k = signalFastFourierTransform[i + 1] ** j
            F_l = signal[-j + 1] ** i
            F1 = signalFastFourierTransform[1] ** (i + j)
            d_ij = F_k * F_l / F1
            d0 = d_ij.real
            d1 = d_ij.imag
            vectorFastFourierCoeficients[indexVector] = d0
            vectorFastFourierCoeficients[indexVector + 1] = d1
            indexVector += 2

    return vectorFastFourierCoeficients