#We import the libraries used
import cv2
import os

#We are goint to work with relative paths, otherwise we have had problems

relative_path = "Datos_Muestra"
detection_types =["spot", "worm", "track"]

def rename_files (i, image_name, relative_path, detection_type):
    """Move images to the detection_type _renamed folder

    Args:
        i (_int_): name of the new images
        image_name (_str_): original image name
        relative_path (_str_): relative path
        detection_type (_str_): muon type
    """
    image = cv2.imread(os.path.join(os.path.join(relative_path, detection_type),image_name))
    cv2.imwrite(f"{relative_path}/{detection_type}_renamed/{i:03d}.jpg", image)

#-----------------------------------------------------------------------------MAIN-----------------------------------------------------------------------------#
def main():
    """Main function. Renames the original images from 000 to 499"""
    for detection_type in detection_types:
        for i, image_name in enumerate(os.listdir(os.path.join(relative_path, detection_type))):
            rename_files(i, image_name, relative_path, detection_type)


if __name__ == '__main__':
    main()


