## Descripción

Este repositorio contiene scripts en Python para generar un dataset. El proceso implica la preparación de imágenes de spots, tracks y worms ubicadas en la carpeta Datos_Muestra. Las imagenes originales han sido extraidas de [https://www-old.wipac.wisc.edu/deco/data](https://www-old.wipac.wisc.edu/deco/data)

## Pasos para Generar el Dataset

1. Asegúrate de tener las carpetas `spot`, `track` y `worm` dentro de la carpeta `wrk_dir/Datos_Muestra` con las imágenes del dataset. En este caso `wrk_dir` será el directorio de trabajo.

2. Ejecuta los siguientes scripts en orden desde `wrk_dir`

   - `py_rename_files_mine.py`
   - `py_crop_images_mine.py`
   - `py_resize_images_mine.py`
   - `py_normalized_images_mine.py`
   - `py_modified_dataset_mine.py`
   - `py_validate_modified_dataset.py`

---

## Description

This repository contains Python scripts to generate a dataset. The process involves preparing images of spots, tracks, and worms located in the `wrk_dir/Datos_Muestra` folder. The original images have been extracted from [https://www-old.wipac.wisc.edu/deco/data](https://www-old.wipac.wisc.edu/deco/data).

## Steps to Generate the Dataset

1. Make sure to have the `spot`, `track`, and `worm` folders inside the `wrk_dir/Datos_Muestra` directory with the dataset images. Here, `wrk_dir` represents the working directory.

2. Execute the following scripts in order from `wrk_dir`:

   - `py_rename_files_mine.py`
   - `py_crop_images_mine.py`
   - `py_resize_images_mine.py`
   - `py_normalized_images_mine.py`
   - `py_modified_dataset_mine.py`
   - `py_validate_modified_dataset.py`