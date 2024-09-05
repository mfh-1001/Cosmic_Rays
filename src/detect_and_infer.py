#Importamos primero las librerias necesarias

import cv2
import os
from datetime import datetime
from ultralytics import YOLO

#Cargamos el modelo. Modificar la ruta donde se encuentre tu modelo.
model = YOLO("path/to/your/model")

# Inicializa la cámara 0 es la camara predeterminada de la maquina
cap = cv2.VideoCapture(1)

# Definir el tiempo de duración (en segundos)
duracion_segundos = 3600 

# Obtener el tiempo de inicio
tiempo_inicio = datetime.now()

# Carpeta donde se guardarán las detecciones
carpeta_detecciones = "detections"
# Carpeta donde se guardarán las inferencias
carpeta_inferencia = "detections_infered"

# Contador de imágenes almacenadas
contador_imagenes = 0
limite_imagenes = 100


# Crear la carpeta si no existe
if not os.path.exists(carpeta_detecciones):
    os.makedirs(carpeta_detecciones)

if not os.path.exists(carpeta_inferencia):
    os.makedirs(carpeta_inferencia)

try:
    while True:
        # Comprobar el tiempo transcurrido
        tiempo_actual = datetime.now()
        tiempo_transcurrido = tiempo_actual - tiempo_inicio
        if tiempo_transcurrido.total_seconds() >= duracion_segundos:
            print("Tiempo de captura alcanzado. Saliendo ...")
            break
        
        # Lee el frame
        ret, frame = cap.read()
        if not ret:
            print("No se puede recibir frame. Saliendo ...")
            break
        
        # Definir la región de interés (ROI) para incluir solo hasta la columna 550 y eliminar falsas detecciones
        roi = frame[:, :550]
        
        # Convertir la ROI a escala de grises
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Comprueba si algún pixel supera el umbral de 50 en la ROI
        if cv2.countNonZero(cv2.threshold(gray_roi, 50, 255, cv2.THRESH_BINARY)[1]) > 0:
            # Genera un nombre de archivo único basado en la fecha y hora actuales
            timestamp = tiempo_actual.strftime("%Y%m%d_%H%M%S_%f")
            file_name = f"{carpeta_detecciones}/detection_{timestamp}.jpg"

            contador_imagenes += 1
            if contador_imagenes >= limite_imagenes:
                print("Límite de imágenes alcanzado. Saliendo ...")
                break
            
            # Guarda la imagen
            cv2.imwrite(file_name, frame)
            print(f"Imagen con detección guardada: {file_name}")

            results = model([file_name])  # return a list of Results objects
            results[0].save(filename=f"{carpeta_inferencia}/detection_{timestamp}.jpg")


        
        # Muestra el frame
        cv2.imshow("Frame", frame)
        
        # Sale del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Tecla 'q' presionada. Saliendo ...")
            break

finally:
    # Libera la cámara y cierra todas las ventanas
    cap.release()
    cv2.destroyAllWindows()