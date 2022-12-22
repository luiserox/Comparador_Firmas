import cv2
import os
import numpy as np
import base64
from pdf2image import convert_from_bytes
import matplotlib.pyplot as plt

#Función para ubicar región probable de firma basado en reconocimiento facial de la foto en CI
def region_firma(image):

    #Cargar data para modelo de reconocimiento facial
    cascPathface = os.path.dirname(
    cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"

    #Modelo clasificador de imagen con data de reconocimiento facial
    faceCascade = cv2.CascadeClassifier(cascPathface)

    #Pasar a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #Detectar ubicación de segmentos semejantes a rostros
    faces = faceCascade.detectMultiScale(gray,
                                            scaleFactor=1.1,
                                            minNeighbors=5,
                                            minSize=(65, 65),
                                            flags=cv2.CASCADE_SCALE_IMAGE)

    #Cantidad de rostros encontrados
    amount_found = len(faces)

    #Variable de rostro más grande encontrado
    max_square = 0
    #Revisar 3 rotaciones de 90 grados hasta encontrar un rostro lo suficientemente grande
    for i in range(1,4):
        #Sólo buscar si no hay rostros encontrados o los rostros encontrados son pequeños
        if amount_found == 0 or (max(faces[:,3])/max(image.shape))<0.05:
            #Si el rostro existe pero es pequeño, asignar como rostro más grande hasta ahora
            if amount_found != 0:
                max_square = max(faces[:,3])
            
            #Guardar versiones temporales de imagen rotada
            temp_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            temp_gray = cv2.cvtColor(temp_image, cv2.COLOR_BGR2GRAY)

            #Guardar versiones temporales de rostros encontrados en imagen rotada
            temp_faces = faceCascade.detectMultiScale(temp_gray,
                                            scaleFactor=1.1,
                                            minNeighbors=5,
                                            minSize=(65, 65),
                                            flags=cv2.CASCADE_SCALE_IMAGE)
            amount_found = len(temp_faces)

            #Si se encontraron rostros más grandes que el actual, guardar el rostro encontrado
            if amount_found != 0 and max(temp_faces[:,3]) > max_square:
                image = temp_image
                gray = temp_gray
                faces = temp_faces
                amount_found = len(faces)
                max_square = max(faces[:,3]) 

    #Sólo proceder si se encontró un rostro
    if amount_found != 0 :
        #Guardar rostro más grande encontrado
        face = faces[faces[:,3]==max(faces[:,3])]

        #Recorrer los rostros, aunque debería haber sólo uno así que esto es para extraer los datos de las coordenadas del rostro
        for (x, y, width, height) in face:    
            # Mover las coordenadas del rostro en CI a posición probable de firma en CI
            x_firma = x + int(height*1.15)
            y_firma = y + width
            height_firma = int(height*4.5)
            width_firma = int(width*2)

            #Recortar y retornar firma de imagen original. Se tiene cuidado de no exceder el tamaño de la imagen original
            image = image[y_firma:min(y+width_firma , image.shape[0]) , x_firma:min(x+height_firma , image.shape[1])]
            return image

    #Retornarn falso si no hay rostros encontrados
    return False