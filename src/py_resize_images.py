import cv2
import os

relative_path = "Datos_Muestra"
detection_types =["spot", "worm", "track"]

def resize_images (image_name, detection_type):
    """Resized the images to 50x50

    Args:
        image_name (_str_): original image name
        detection_type (_type_): detection type
    """
    image = cv2.imread(f"{relative_path}/{detection_type}_renamed_cropped/{image_name}")
    resized_image = cv2.resize(image, (50,50))
    cv2.imwrite(f"{relative_path}/{detection_type}_renamed_cropped_resized/{image_name}", resized_image)

#-----------------------------------------------------------------------------MAIN-----------------------------------------------------------------------------#
def main():
    """Main function resized images to 50x50"""
    for detection_type in detection_types:
        for image_name in os.listdir(f"{relative_path}/{detection_type}_renamed_cropped"):
            resize_images(image_name, detection_type)

if __name__ == '__main__':
    main()

