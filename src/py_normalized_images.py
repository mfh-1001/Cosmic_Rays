import cv2 
from pytesseract import pytesseract 
import os 
import numpy as np 
from scipy.signal import find_peaks 
import scipy.ndimage 


relative_path = "Datos_Muestra" 
detections_types = ["spot", "track", "worm"]
A_scale_values, C_scale_values = [145, 740], [690, 715] #The regions of the image we want.
A_scale, C_scale = [162, 688], [659, 714]
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe" 
pytesseract.tesseract_cmd = path_to_tesseract 

def crop_scale_values(image_name, detection_type):
    """This function crops the scale color of the images

    Args:
        image_name (_str_): image name
        detection_type (str_): detection type

    Returns:
        _'numpy.array'_: scale value image
    """
    image = cv2.imread(f"{relative_path}/{detection_type}_renamed/{image_name}") #Image of the _renamed folder.
    cropped_scale_values_image = image[C_scale_values[1]:A_scale_values[1], A_scale_values[0]:C_scale_values[0]]
    _, cropped_scale_values_image = cv2.threshold(cropped_scale_values_image, 225, 255, cv2.THRESH_BINARY)
    #All pixels with values lower than 225 are set to 0 and 1 if they are larger.
    black_pixels = np.array(np.where(cropped_scale_values_image == 0))[:-1, :]
    #Finds all the black pixels from the previus image.

    #We calculate the maximum and minimum coordinates where black pixels exist.
    offset = 3
    minimum_y = black_pixels[0, :].min() - offset
    maximum_y = black_pixels[0, :].max() + offset
    minimum_x = black_pixels[1, :].min() - offset
    maximum_x = black_pixels[1, :].max() + offset*5
   
    cropped_scale_values_image = cropped_scale_values_image[minimum_y: maximum_y, minimum_x: maximum_x]
    return cropped_scale_values_image



def get_scale_info(cropped_scale_image):
    """This function calculates the step of the scale value and its maximum value.

    Args:
        cropped_scale_image ('numpy.array'): cropped scale image calculated using previous function.

    Returns:
        scale_maximum_visible_value: last visible value of the scale.
        scale_step: scale step.
    """    
    original_cropped_scale_image = cropped_scale_image.copy()
    kernel = np.ones((5, 5), np.uint8) 
    cropped_scale_image_eroded = cv2.erode(cropped_scale_image, kernel, iterations=2)
    #This operation set to zero those pixels that are not surrounded by 5x5 ones
    cropped_scale_image_eroded_gray = cv2.cvtColor(cropped_scale_image_eroded, cv2.COLOR_BGR2GRAY)
    #Convert the image in grey scale
    _, cropped_scale_image_threshold = cv2.threshold(cropped_scale_image_eroded_gray, 0, 255, cv2.THRESH_BINARY)
    #Convert the image un black and white

    contours, _ = cv2.findContours(cv2.bitwise_not(cropped_scale_image_threshold), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_sorted = sort_contours(contours)
    #Calculates all the outline of the images, which must be in binary. It returns a 2 dim matrix, one for the contours and one for its coordinates.

    numbers_found = []
    for c in contours_sorted:
        x, y, w, h = cv2.boundingRect(c) #Calculates the smallest rectangle containing the contour.
        #x and y set the upper left vertex of the rectangle, w = width and h = height.
        cv2.rectangle(cropped_scale_image, (x, y), (x+w, y+h), (0, 0, 255), 1)
   
        cropped_scale_sub_image = original_cropped_scale_image[y:y+h, x:x+w] #Extract the region of interest
        kernel = np.ones((3, 3), np.uint8) 
        cropped_scale_sub_image = cv2.morphologyEx(cropped_scale_sub_image, cv2.MORPH_OPEN, kernel, iterations=1)#Image processing
        number = pytesseract.image_to_string(cropped_scale_sub_image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
        #Reads the digit of the image

        if number == '':
            numbers_found.append(int(0))
        else:
            numbers_found.append(int(number.replace('\n', '')))
        #Add to a list the found numbers. If no one is detected, add a 0.

    differences = [abs(j-i) for i, j in zip(numbers_found[:-1], numbers_found[1:])]#Calculate the posible step values
    if len(set(differences)) != 1:
        mode = max(set(differences), key=differences.count)#Calculate the modal step value
        indexes = np.array(differences) != mode 
        first_true_index = np.nonzero(indexes==True)[0][0]
        indexes_to_change = list(np.arange(first_true_index, len(indexes))+1)
        for index in indexes_to_change:
            numbers_found[index] = numbers_found[index-1]+mode

    scale_maximum_visible_value = numbers_found[-1]   #Maximux scale value
    differences = [abs(j-i) for i, j in zip(numbers_found[:-1], numbers_found[1:])]
    scale_step = max(set(differences), key=differences.count)
    return scale_maximum_visible_value, scale_step

def get_scale_span(image_name, detection_type, scale_step, scale_maximum_visible_value):#
    """Calculates the maximum value of the scale. It needs external functions.

    Args:
        image_name ('str'): image name.
        detection_type ('str'): detection type.
        scale_step ('int'): scale step.
        scale_maximum_visible_value ('int'): maximum scale value in axis.

    Returns:
        scale_span: actual maximum scale value.
    """    
    image = cv2.imread(f"{relative_path}/{detection_type}_renamed/{image_name}")
    cropped_scale_image = image[A_scale[1]:C_scale[1], A_scale[0]:C_scale[0]]#We only want colour scale of the image.
    cropped_scale_image = cv2.cvtColor(cropped_scale_image, cv2.COLOR_BGR2GRAY)#Grey scale.
    v_projection = get_projection(cropped_scale_image, 0)#Highlight vertical values¿?
    v_peaks = find_vertical_peaks(v_projection)#Find vertical values.
    differences = [abs(j-i) for i, j in zip(v_peaks[:-1], v_peaks[1:])]
    pixels_per_step = max(set(differences), key=differences.count)#Modal value.
    pixels_left = cropped_scale_image.shape[1] - v_peaks[-1] #Pixeles from the las peak to the end.

    if pixels_left > pixels_per_step:
        pixels_left = pixels_left - pixels_per_step

    if (pixels_left == pixels_per_step) or (pixels_left-1 == pixels_per_step) or (pixels_left+1 == pixels_per_step):
        scale_span = scale_maximum_visible_value
    else:
        missing_scale = int(round((pixels_left*scale_step)/pixels_per_step, 0))
        scale_span = scale_maximum_visible_value + missing_scale
    return scale_span

#------------------------------------------Functions used in the previous one---------------------------------------------------#
def get_projection(image, axis=0): 
    """Highlight some characteristics in one axis.

    Args:
        image ('numpy.ndarray'): image.
        axis (int, optional): 1 for horizontal axis 0 for vertical. Defaults to 0.

    Returns:
        projection: projections of the image.
    """    

    relief = image.mean(axis=axis)
    smoothed = scipy.ndimage.gaussian_filter(relief, sigma=2.0)
    baseline = scipy.ndimage.gaussian_filter(relief, sigma=10.0)
    projection = baseline - smoothed
    return projection

def find_vertical_peaks(v_projection):
    """Finds the peaks in a vertical projection.

    Args:
        v_projection ('numpy.ndarray'): vertical projection.

    Returns:
        vertical peaks: vertical peaks.
    """    

    v_peaks, _ = find_peaks(v_projection, distance=43) #43 is an arbitray minimal distance between peaks
    return v_peaks

def sort_contours(cnts, method="left-to-right"):#Sort contours in the specified way
    """Sorts the contours in the specified way

    Args:
        cnts ('numpy.ndarray'): contours
        method (str, optional): Way to sort the countours. Defaults to "left-to-right".

    Returns:
        cnts('numpy.ndarray'): sorted contours
    """    
    reverse = False
    i = 0
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b:b[1][i], reverse=reverse))
    return cnts

def normalize_image(image_name, detection_type, scale_span):
    """Normalized the image in the correct range. It allows to compare different images in the same scale.

    Args:
        image_name ('str'): image name
        detection_type ('str'): detection type
        scale_span ('int'): scale span
    """    
    image_cropped = cv2.imread(f"{relative_path}/{detection_type}_renamed_cropped_resized/{image_name}")
    image_cropped_gray = cv2.cvtColor(image_cropped, cv2.COLOR_RGB2GRAY)
    image_normalized = cv2.normalize(image_cropped_gray, None, alpha=0, beta=scale_span, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    cv2.imwrite(f"{relative_path}/{detection_type}_renamed_cropped_resized_normalized/{image_name}", image_normalized)



def main():
    """Read the cropped images and normalize them by extracting their maximum scale value.""" 
    #We normalize the images to a correct format of black and white.
    for detection_type in detections_types:
        for image_name in os.listdir(f"{relative_path}/{detection_type}_renamed"):
            cropped_scale_values_image = crop_scale_values(image_name, detection_type)
            scale_maximum_visible_value, scale_step = get_scale_info(cropped_scale_values_image)
            scale_span = get_scale_span(image_name, detection_type, scale_step, scale_maximum_visible_value)
            normalize_image(image_name, detection_type, scale_span)


if __name__ == '__main__':
    main()
