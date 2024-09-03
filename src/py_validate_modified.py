#First we import all the libraries.
import cv2 
from pytesseract import pytesseract 
import os 
import numpy as np 
from scipy.signal import find_peaks 
import scipy.ndimage 
import random
import csv
import re 
import collections

relative_path = "Datos_Muestra" 
detections_types = ["spot", "track", "worm"]
A_scale_values, C_scale_values = [145, 740], [690, 715] #The regions of the image we want.
A_scale, C_scale = [162, 688], [659, 714]


def validate_muons_integration(file_path):#Select an imagen an set it to black and white to visually validate the integration.
    """Transform an image into black and white in order to validate visually that the integration is successful.

    Args:
        file_path ('str'): path to the image we want to validate
    """    
    match = re.search(r'output_(\d+)\.png', file_path)
    if match:
        image_number = match.group(1)
    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    image_threshold = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY)[1]
    cv2.imwrite(f"modified_dataset_threshold/img{int(image_number):03d}.png", image_threshold)


#---------------------------------------------------------MAIN----------------------------------------------------------------------#
def main():
    """Finally, it validates the process by creating a new dataset with the images generated in black and white."""    
    #We transform the previous dataset to black and white to visually validate the process
    for filename in os.listdir("modified_dataset"):
        #Get the full path to the file
        file_path = os.path.join("modified_dataset", filename)
        # Check if the file is a regular file (i.e. not a directory)
        if os.path.splitext(file_path)[1] == '.png':
            validate_muons_integration(file_path)


if __name__ == '__main__':
    main()
