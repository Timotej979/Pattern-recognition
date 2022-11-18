from thresholding import *
from enum import Enum

class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3
    NOWHERE = 4

class Searcher():
    def __init__(self, inputImage):
        """Initialize shape searcher in given binary image"""
        self.inputImage = inputImage
        self.shapes = []

        # Image dimensions
        self.m = inputImage.shape[0]
        self.n = inputImage.shape[1]

        # Initialize list of  checked lements
        self.LCE = []

        # Initialize pixel side notes
        self.pixelNotes = np.zeros((self.m, self.n), dtype=np.unicode_)
        for i in range(self.m):
            for j in range(self.m):
                self.pixelNotes[i, j] = "N"

    def searchShapes(self):
        """Finds all shapes on image"""
        m, n = self.inputImage.shape
        self.shapes = []
        for y in range(m):
            self.LCE = []
            for x in range(n):
                if self.isStartingPoint(x, y):
                    self.shapeFollower(x, y)

        # The first shape of an image is usually the image frame therefore we delete it
        if len(self.shapes) > 1:
            self.shapes = self.shapes[1:]

    def isStartingPoint(self, x, y):
        """Check if the given point is a valid starting point of a shape"""
        if self.pixelNotes[y, x] == "N" and \
           (len(self.LCE) == 0 or self.LCE[-1] != self.inputImage[y, x]):
            return True
        elif self.pixelNotes[y, x] == "A":
            self.LCE.append(self.inputImage[y, x])
        elif (self.pixelNotes[y, x] == "D" and \
              len(self.LCE) != 0 and \
              self.LCE[-1] == self.inputImage[y, x]):
            self.LCE.pop()
        return False

    def checkVicinity(self, x_z, y_z):
        """If the starting point vicinity is of pixles is in different colors it is not a valid point"""
        pixelNote = self.inputImage[y_z, x_z]
        if self.inputImage[y_z, x_z + 1] != pixelNote and \
           self.inputImage[y_z, x_z - 1] != pixelNote and \
           self.inputImage[y_z + 1, x_z] != pixelNote and \
           self.inputImage[y_z - 1, x_z] != pixelNote:
               return False
        return True

    def shapeFollower(self, x_z, y_z):
        """Follow the shape with starting point (x_z, y_z)"""
        x_o = x_z
        y_o = y_z

        check = self.checkVicinity(x_z, y_z)
        if check == False:
            return 0

        codes = []
        points = [(x_z, y_z)]

        enter = Direction.NOWHERE

        while True:
            exit = self.move(x_o, y_o, enter)
            self.setPixelNote(enter, exit, x_o, y_o)
            if exit == Direction.UP:
                y_o -= 1
            elif exit == Direction.DOWN:
                y_o += 1
            elif exit == Direction.LEFT:
                x_o -= 1
            elif exit == Direction.RIGHT:
                x_o += 1

            codes.append(exit.value)
            points.append((x_o, y_o))
            enter = exit
            if x_o == x_z and y_o == y_z:
                break

        startingPoint = (x_z, y_z)
        obris = {"ZT": startingPoint, "codes": codes, "points": points}
        self.shapes.append(obris)
        return 0

    def view(self, x_o, y_o, direction):
        """Check if the pixel in direction 'Direction' is part of the same shape as the point (x_o, y_o) accounting for edge cases"""
        if direction == Direction.RIGHT:
            if x_o + 1 >= self.inputImage.shape[1]:
                return False
            elif self.inputImage[y_o, x_o + 1] != self.inputImage[y_o, x_o]:
                return False
            else:
                return True
        elif direction == Direction.DOWN:
            if y_o + 1 >= self.inputImage.shape[0]:
                return False
            elif self.inputImage[y_o + 1, x_o] != self.inputImage[y_o, x_o]:
                return False
            else:
                return True
        elif direction == Direction.LEFT:
            if x_o == 0:
                return False
            elif self.inputImage[y_o, x_o - 1] != self.inputImage[y_o, x_o]:
                return False
            else:
                return True
        elif direction == Direction.UP:
            if y_o == 0:
                return False
            elif self.inputImage[y_o - 1, x_o] != self.inputImage[y_o, x_o]:
                return False
            else:
                return True
    
    def move(self, x_o, y_o, enter):
        """Move along the shape from point (x_o, y_o) into the next point by left priority rule"""
        if enter == Direction.NOWHERE or enter == Direction.RIGHT:
            priority = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        elif enter == Direction.DOWN:
            priority = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        elif enter == Direction.LEFT:
            priority = [Direction.DOWN, Direction.LEFT, Direction.UP, Direction.RIGHT]
        elif enter == Direction.UP:
            priority = [Direction.LEFT, Direction.UP, Direction.RIGHT, Direction.DOWN]

        for direction in priority:
            if self.view(x_o, y_o, direction):
                return direction

    def setPixelNote(self, enter, exit, x_o, y_o):
        """Set pixel note of shape point (x_o, y_o) depending on its previous pixel note and enter/exit direction from point"""

        previous = self.pixelNotes[y_o, x_o]

        if enter == Direction.UP or enter == Direction.LEFT or enter == Direction.NOWHERE:
            if exit == Direction.UP or exit == Direction.RIGHT:
                new = "A"
            elif exit == Direction.DOWN or exit == Direction.LEFT:
                new = "T"
        elif enter == Direction.DOWN or enter == Direction.RIGHT:
            if exit == Direction.UP or exit == Direction.RIGHT:
                new = "T"
            elif exit == Direction.DOWN or exit == Direction.LEFT:
                new = "D"

        # If the previous pixel note is 'N', we are on this point the first time and the new pixel note is writen by above rule. Otherwise the pixel note is set by the state table:

        par = previous + new

        if par == "DA" or par == "AD" or par == "TT":
            new = "T"
        elif par == "DT" or par == "TD" or par == "DD":
            new = "D"
        elif par == "AT" or par == "TA" or par == "AA":
            new = "A"

        self.pixelNotes[y_o, x_o] = new
        return 0

    def getLongestShape(self):
        """Returns the longest shape from the found shapes, which usualy is the biggest object on the image"""
        max = 0
        maxIndex = 0
        for i in range(len(self.shapes)):
            if(len(self.shapes[i]["codes"]) > max):
                max = len(self.shapes[i]["codes"])
                maxIndex = i
        
        return self.shapes[maxIndex]

    def drawAllShapes(self, grayScaleInterval):
        """Returns an image with all shapes drawn. Every shape has a different gray value on the final picture"""
        shapeImage = np.zeros_like(self.inputImage, 'uint8')
        
        # Add key pointsNum to set it to the number of points in a shape
        for i in range(len(self.shapes)):
            self.shapes[i]['pointsNum'] = len(self.shapes[i]['points'])

        # Sort shapes by its length from longest to shortest
        self.shapes = sorted(self.shapes, key = lambda d: d["pointsNum"]) 

        colorCounter = 0
        for shape in self.shapes:
            # Grayscale value range on interval [startColor, stopColor] / linear transformation of inputed interval
            grayColor = round( colorCounter * (grayScaleInterval[1] - grayScaleInterval[0])/len(self.shapes) + grayScaleInterval[0] )
            colorCounter = colorCounter + 1
            for point in shape.get('points'):
                shapeImage[point[1]][point[0]] = grayColor 

        return shapeImage

    def drawShape(self, shape, grayColor):
        """Draws the given shape on the picture of the same resolution as the inputImage"""
        shapeImage = np.zeros_like(self.inputImage)

        for point in shape.get('points'):
            shapeImage[point[1]][point[0]] = grayColor

        return shapeImage