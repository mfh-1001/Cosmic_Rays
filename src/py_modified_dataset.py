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


# Background images dimensions (for normalization)
bg_width = 640
bg_height = 480


def create_modified_dataset(background_dir, image_dirs, output_dir, image_id, image_name, csv_path, csv_normalized_path):
    """Creates the modified dataset. It adds from 1 to 5 detection images randomly to a black noisy background image.
    The background image are selected randomly from a set of background images obtained with the webcam used in the project.

    Args:
        background_dir ('str'): background directory containing multiple background images.
        image_dirs ('str'): image directories.
        output_dir ('str'): output directory which storage the new dataset.
        image_id ('int'): image identifier number.
        image_name ('str'): image path.
        csv_path ('str'): csv directory. It will save the characteristics of the new dataset.
        csv_normalized_path ('str'): path to save the normalized coordinates.

    Returns:
        num_images('int'): number of events added to the background image.
    """

    # Load all background images
    background_images = [os.path.join(background_dir, f) for f in os.listdir(background_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # Initialize the CSV writers
    with open(csv_path, mode='a', newline='') as csv_file, open(csv_normalized_path, mode='a', newline='') as csv_norm_file:
        fieldnames = ['image_id', 'image_path', 'muon path', 'muon_type', 'center_x', 'center_y', 'w', 'h']
        norm_fieldnames = ['image_id', 'image_path', 'muon path', 'muon_type', 'norm_center_x', 'norm_center_y', 'norm_w', 'norm_h']
        
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, dialect='excel')
        norm_writer = csv.DictWriter(csv_norm_file, fieldnames=norm_fieldnames, dialect='excel')

        # Write the header row if the file is empty
        if os.stat(csv_path).st_size == 0:
            writer.writeheader()
        if os.stat(csv_normalized_path).st_size == 0:
            norm_writer.writeheader()

        # Loop through the image directories and load the small images
        images_path = []
        for image_dir in image_dirs:
            filenames = os.listdir(image_dir)
            for filename in filenames:
                image_path = os.path.join(image_dir, filename)
                images_path.append(image_path)
        # Shuffle the images
        random.shuffle(images_path)

        # Select a random number of images to place on the background
        num_images = random.choice([1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 5])

        if num_images == 0:
            # If no images are selected, save the background as-is
            selected_background_path = random.choice(background_images)
            background = cv2.imread(selected_background_path)
            cv2.imwrite(f"{output_dir}{image_name}", background)
            return

        # Select the images to place on the background
        selected_images_paths = images_path[:num_images]

        # Select a random background image
        selected_background_path = random.choice(background_images)
        background = cv2.imread(selected_background_path)

        # Randomly place the images on the background
        for image_path in selected_images_paths:
            image = cv2.imread(image_path)
            file_path = image_path.replace("\\", "/")
            file_name = file_path.split("/")[-1]
            file_dir = file_path.split(file_name)[0]
            file_dir = file_dir.split("/")[-2] + "/"
            muon_path = file_dir + file_name
            directory = os.path.dirname(image_path)
            muon_type = os.path.basename(directory).split("_")[0]
            x = random.randint(0, background.shape[1] - image.shape[1])
            y = random.randint(0, background.shape[0] - image.shape[0])
            w = image.shape[1]
            h = image.shape[0]

            # Calculate the center coordinates
            center_x = x + w // 2
            center_y = y + h // 2

            # Calculate normalized coordinates
            norm_center_x = center_x / bg_width
            norm_center_y = center_y / bg_height
            norm_w = w / bg_width
            norm_h = h / bg_height

            im_intermediate = background[y:y+h, x:x+w]
            im_intermediate[image > 20] = image[image > 20]
            background[y:y+h, x:x+w] = im_intermediate  # Background image is modified adding the detections

            # Add a row to the CSV file for the placed image
            writer.writerow({'image_id': image_id, 'image_path': f"output_{image_id}.png", 'muon path': muon_path, 'muon_type': muon_type, 
                             'center_x': center_x, 'center_y': center_y, 'w': w, 'h': h})
                             
            # Add a row to the normalized CSV file for the placed image
            norm_writer.writerow({'image_id': image_id, 'image_path': f"output_{image_id}.png", 'muon path': muon_path, 'muon_type': muon_type, 
                                  'norm_center_x': norm_center_x, 'norm_center_y': norm_center_y, 'norm_w': norm_w, 'norm_h': norm_h})

        # Save the resulting image
        cv2.imwrite(f"{output_dir}{image_name}", background)
        return num_images

    
def count_files(path):
    """Counts the number of files in a given path.

    Args:
        path ('str'): path we want to use.

    Returns:
        ('int'): number of files
    """    
    return sum([len(files) for _, _, files in os.walk(path) if files])


#---------------------------------------------------------MAIN----------------------------------------------------------------------#
def main():
    """It creates 1500 new images simulating the actual detections by adding randomly from 1 to 5 detection images to a black noisy
    image.
    
    """    
    #We create the new modified dataset including the detections into the black noisy background image

    #Eliminate the current files in the directory
    
    for filename in os.listdir("modified_webcam_dataset"):
        # Get the full path to the file
        file_path = os.path.join("modified_webcam_dataset", filename)
        # Check if the file is a regular file (i.e. not a directory)
        if os.path.isfile(file_path):
            # Delete the file
            os.remove(file_path)
    
    generated_numbers = []
    num_files = 0
    for directory in ["Datos_Muestra/spot_renamed_cropped_resized_normalized", "Datos_Muestra/track_renamed_cropped_resized_normalized", 
                        "Datos_Muestra/worm_renamed_cropped_resized_normalized"]:
        num_files += count_files(directory)

    for i in range(num_files):
        
        generated_number = create_modified_dataset(f"background_images", 
                                                    ["Datos_Muestra/spot_renamed_cropped_resized_normalized", 
                                                    "Datos_Muestra/track_renamed_cropped_resized_normalized", 
                                                    "Datos_Muestra/worm_renamed_cropped_resized_normalized"], 
                                                    "modified_webcam_dataset/", i, f"output_{i}.png", 
                                                    "modified_webcam_dataset/dataset_info.csv",
                                                    "modified_webcam_dataset/dataset_info_normalized.csv")
        if generated_number == None:
            generated_numbers.append(0)    
        else:
            generated_numbers.append(int(generated_number))

    # Count the occurrences of each element in the list
    counts = dict(sorted(collections.Counter(generated_numbers).items()))

    #Escribe cuantas imagenes con varios tipos de detecciones a la vez hay
    # Open a file in write mode
    with open("modified_webcam_dataset/output.txt", "w") as file:
        # Redirect the output of the print function to the file object
        print("Element: Count", file=file)
        for element, count in counts.items():
            print(f"{element}: {count}", file=file)
            print(f"{element}: {count}")



if __name__ == '__main__':
    main()
