from email.mime import image
import numpy as np
import matplotlib.pyplot as plt
import cv2

importPicture = cv2.imread("parrots.jpg")
print(importPicture, importPicture.dtype, importPicture.min(), importPicture.max())