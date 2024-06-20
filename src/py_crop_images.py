import cv2
import os

#We use relative paths
relative_path = "Datos_Muestra"
detection_types = ["spot", "track", "worm"]
#The coordinates of the image that we want to keep
A, C = [100, 80], [720, 625]

def crop_image(image_name, detection_type):
    """We only want the detection perse

    Args:
        image_name (_str_): image name
        detection_type (_str_): detection type
    """
    image = cv2.imread(f"{relative_path}/{detection_type}_renamed/{image_name}")
    cropped_image = image[A[1]:C[1], A[0]:C[0]]
    cv2.imwrite(f"{relative_path}/{detection_type}_renamed_cropped/{image_name}",cropped_image)

#-----------------------------------------------------------------------------MAIN-----------------------------------------------------------------------------#
def main():
    for detection_type in detection_types:
        for image_name in os.listdir(f"{relative_path}/{detection_type}_renamed"):
            crop_image(image_name, detection_type)

if __name__ == '__main__':
    main()