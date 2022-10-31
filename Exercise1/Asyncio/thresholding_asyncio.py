import numpy as np
import matplotlib.pyplot as plt

class DigitalImageProcessing:

    def __init__(self, grayScaleImage):
        self.grayScaleImage = grayScaleImage

    async def calculateHistogram(self):
        """Calculate histogram of a grayscale image.
        @param grayImage : uint8 2D numpy array of variable size
        output: image histogram"""
        histogram = np.zeros((256,), dtype="float64")
        for gray_threshold in range(256):
            pixel_num = np.sum(self.grayScaleImage == gray_threshold)
            histogram[gray_threshold] = pixel_num
        self.imageHistogram = histogram

    # Can not be async because of plt.show() is synchronous
    def drawHistogram(self):
        """Draws calculated histogram.
        @param histogram : 1D numpy array of variable size and type"""
        element_num = self.imageHistogram.shape[0]
        plt.figure()
        plt.title("Histogram")
        plt.bar(np.arange(element_num), self.imageHistogram)
        plt.xlabel("Luminosity")
        plt.ylabel("Number of pixels")
        plt.grid(True)
        return 0

    async def setThreshold(self):
        """Sets threshold of a grayscale image by maximizing information.
        @param grayImage : Image we are setting a threshold to
        output: Value of threshold, which maximizes information"""
        # Calculate number of pixels in image
        n = self.grayScaleImage.shape[0] * self.grayScaleImage.shape[1]

        # Calculate distribution of relative frequencies, P
        P = self.imageHistogram / n

        # Initialize vector where we save our  information
        # For every possible value of threshold
        information = np.zeros_like(self.imageHistogram)

        # Calculate information at every possible value of threshold
        # Set threshold value which maximizes information
        for t in range(1, 254):
            normalizedP = np.sum(P[:t])
            
            firstFactor = P[:t+1]/normalizedP
            firstFactor[(firstFactor == 0) | (np.isnan(firstFactor))] = 1
            H0 = - np.sum( np.dot( firstFactor, np.log2(firstFactor) ) )

            secondFactor = P[t+1:]/(1-normalizedP)
            secondFactor[(secondFactor == 0) | (np.isnan(secondFactor))] = 1
            H1 = - np.sum( np.dot( secondFactor, np.log2(secondFactor) ) )

            information[t] = H0 + H1

        # Calculate information at every possible threshold:
        # Search for threshold value where the information is maximized
        t = np.argmax(information)
        self.imageThreshold = t