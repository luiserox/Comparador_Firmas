import base64
import sys
import cv2
import numpy as np
from pdf2image import convert_from_bytes
from skimage import measure, morphology
from skimage.measure import regionprops

from signature_detect.extractor import Extractor

import matplotlib.pyplot as plt

from recon_firma import region_firma

#Función que invierte color de la imagen
def reverse_color(img):
  return img.max() - img + img.min()

#Función de impresión de imagen
def show_image(img):
    fig, ax = plt.subplots(figsize=(5, 10))
    ax.imshow(img, cmap = 'gray')
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()

#Función para extraer firma de CI en base64
def ci_signature(base64CI):

    #Convertir de base64 (pdf/jpg/png) a imagen (numpy)
    ci_bytes = base64.b64decode(base64CI)
    nparr = np.frombuffer(ci_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #Si CI está en pdf se convierte la primera hoja a imagen
    if image is None:
        ci_images = convert_from_bytes(ci_bytes, dpi=300)
        image = np.array(ci_images[0]) 

    #show_image(image)

    #Función que extrae región probable de firma, basado en ubicación de rostro (foto) en CI
    image = region_firma(image)

    #Retornar falso si no se encontró un rostro en la imagen
    if image is False:
        return False

    #Convertir imagen a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #Filtro gaussiano, hace más continua la imagen
    #blurred = cv2.GaussianBlur(gray, (7, 7), 0) 
    blurred = gray
    #Filtro de umbral adaptable, convierte la imagen de escala de grises en blanco y negro. blockSize es el área tomada para calcular el umbral entre blanco y negro, debe ser impar. C es una constante (double) que se resta del valor promedio de la región (mayor valor simula una imagen más oscura)
    #Esta función ayuda a eliminar el fondo alrededor de la firma
    thresh = cv2.adaptiveThreshold(blurred, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=7, C=1.5)

    #Este conjunto de funciones elimina elementos pequeños de la imagen. min_area_size que debe tener un objeto para mantenerse. amplfier es proporcional al tamaño de los objetos más grandes a ser eliminados, es decir que amplfier crece con el límite superior de tamaño de objetos a mantener en la imagen
    amplfier = 300
    extractor = Extractor(amplfier=amplfier, min_area_size=7)
    labeled_mask = extractor.extract(thresh)

    #Detectar y marcar objetos continuos en la imagen. Es reconocimiento de regiones de interés
    b = labeled_mask
    blobs_firma = b > b.mean()
    b_labels = measure.label(blobs_firma, connectivity=2, background=1)

    #Inicialización de variables de interés sobre dimensiones de la firma
    max_area = 0
    min_x = []
    min_y = []
    max_x = []
    max_y = []

    #Recorrer regiones de interés encontradas en la línea 66 - measure.label(...)
    for region in regionprops(b_labels):
        #Medir dimensiones de región
        h, w = region.image.shape
        area = h*w
        #Calcular tamaño mínimo para región de interés, basado en el tamaño de la imagen original
        min_size = (image.shape[1]*image.shape[0])*0.01

        #Condicional para validar que la región supera el tamaño mínimo, no es desproporcionalmente larga/alta y está en la región superior izquierda de la imagen original
        if (area >= min_size) and (h * 8 > w and w * 10 > h) and region.bbox[3]<image.shape[1]*0.65 and region.bbox[2]<image.shape[0]*0.95:
            #Agregar ubicación de región a lista de interés
            min_x.append(region.bbox[1]) 
            min_y.append(region.bbox[0])
            max_x.append(region.bbox[3])
            max_y.append(region.bbox[2])

            #Actualizar área máxima
            max_area = region.area

    #Tomar firma en la imagen filtrada basado en las regiones de interés, tomando los mínimos y máximos de las coordenadas de las regiones de interés  
    firma = labeled_mask[min(min_y):max(max_y) , min(min_x):max(max_x)]

    #Sólo retornar firma si existen regiones de interés. De lo contrario, retornar False
    if max_area != 0:
        firma = (firma.astype(np.uint8) * 255)
        return firma
    else:
        return False

#Código para hacer pruebas de está función
'''ruts = ['13.237.661','7.394.171', '12.971.928', '10.304.793', '15.721.575', '15.057.662', '15.196.715', '10.474.004', '6.094.215', '12.522.921']

for i in range(1,11):

    with open("CIyPag/Caso{i}/{rut}/CI.txt".format(i=i,rut=ruts[i-1]), "rb") as ci_file:
        base64CI = ci_file.read()
    
    firma = ci_signature(base64CI)
    if firma is not False:
        show_image(firma)'''