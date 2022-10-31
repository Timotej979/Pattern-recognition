import numpy as np
import matplotlib.pyplot as plt
import cv2
import sys



class DigitalImageProcessing():

    def __init__(self, greyImage):
        self.greyImage = greyImage

    def calculateHistogram(self):
        """Calculate histogram of a grayscale image.
        @param greyImage : uint8 2D numpy array of variable size
        output: image histogram"""
        histogram = np.zeros((256,), dtype="float64")
        for grey_threshold in range(256):
            pixel_num = np.sum(self.greyImage == grey_threshold)
            histogram[grey_threshold] = pixel_num
        self.histogram = histogram

    def drawHistogram(self):
        """Draws calculated histogram.
        @param histogram : 1D numpy array of variable size and type"""
        element_num = self.histogram.shape[0]
        plt.figure()
        plt.title("Histogram")
        plt.bar(np.arange(element_num), self.histogram)
        plt.xlabel("Luminosity")
        plt.ylabel("Number of pixels")
        plt.grid(True)
        return 0

    def setThreshold(self):
        """Sets threshold of a grayscale image by maximizing information.
        @param greyImage : Image we are setting a threshold to
        output: Value of threshold, which maximizes information"""
        histogram = self.calculateHistogram(self.greyImage)

        # calculate number of pixels in image
        n = self.greyImage.shape[0] * self.greyImage.shape[1]

        # calculate distribution of relative frequencies, P
        P = histogram / n

        # initialize vector where we save our  information
        # for every possible value of threshold
        information = np.zeros_like(histogram)

        # calculate information at every possible value of threshold
        # set threshold value which maximizes information
        for t in range(1, 254):
            normalizedP = np.sum(P[:t])
            
            firstFactor = P[:t+1]/normalizedP
            firstFactor[(firstFactor == 0) | (np.isnan(firstFactor))] = 1
            H0 = - np.sum( np.dot( firstFactor, np.log2(firstFactor) ) )

            secondFactor = P[t+1:]/(1-normalizedP)
            secondFactor[(secondFactor == 0) | (np.isnan(secondFactor))] = 1
            H1 = - np.sum( np.dot( secondFactor, np.log2(secondFactor) ) )

            information[t] = H0 + H1

        # calculate information at every possible threshold:
        # search for threshold value where the information is maximized
        t = np.argmax(information)
