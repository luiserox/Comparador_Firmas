import base64
import sys
from pdf2image import convert_from_bytes
import cv2
import numpy as np
from skimage import measure, morphology
from skimage.color import label2rgb
from skimage.measure import regionprops
from skimage.filters import threshold_local
import matplotlib.pyplot as plt
from skimage.feature import match_template

#Función de revertir colores en imagen
def reverse_color(img):
  return img.max() - img + img.min()

#Extraer firma de documento pagare (pdf)
def pdf_signature(base64PDF):

    #Convertir pdf base64 en conjunto de imágenes por página
    pdf_bytes = base64.b64decode(base64PDF)
    pdf_images = convert_from_bytes(pdf_bytes, dpi=300)

    #Tomar la imagen de la página 3, donde suele estar la firma
    image = np.array(pdf_images[2])

    #Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #Mejorar continuidad en la imagen
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    ##Filtro de umbral adaptable, convierte la imagen de escala de grises en blanco y negro. blockSize es el área tomada para calcular el umbral entre blanco y negro, debe ser impar. C es una constante (double) que se resta del valor promedio de la región (mayor valor simula una imagen más oscura)
    #Esta función ayuda a eliminar el fondo alrededor de la firma
    thresh = cv2.adaptiveThreshold(blurred, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 7, 5)


    img = thresh
    #Revertir color de imagen 
    img = reverse_color(img)
    #Parametro determina el tamaño de objetos a eliminar. Más pequeño implica mantener objetos más pequeños
    parametro = 0.4

    '''plt.figure(figsize=(10,10))
    plt.imshow(img,cmap='gray')
    plt.show()'''

    #Separar imagen en regiones continuas de interés
    blobs = img > img.mean()
    blobs_labels = measure.label(blobs, background=1)

    #Revisar regiones de interés y encontrar componentes más grandes
    the_biggest_component = 0
    total_area = 0
    counter = 0
    average = 0.0
    for region in regionprops(blobs_labels):
        if (region.area > 10):
            total_area = total_area + region.area
            counter = counter + 1
        if (region.area >= 1000):
            if (region.area > the_biggest_component):
                the_biggest_component = region.area
    
    #Determinar tamaño promedio de regiones
    average = (total_area/counter)

    #Constante para determinar los objetos a eliminar. Aquí se usa el parámetro de la línea 40            
    constant = average/img.shape[0]*img.shape[1] * 7.75 * parametro

    #Función que remueve objetos más pequeños que constante
    b = morphology.remove_small_objects(blobs_labels, constant)

    #Invertir color de imagen
    b = b.max() - b + b.min()

    #Determinar nuevas regiones de interés luego de filtrar objetos pequeños
    blobs_firma = b > b.mean()
    b_labels = measure.label(blobs_firma, connectivity=2, background=1)

    #Recorrer áreas de interés encontradas y extraer región más grande
    area_max = 0
    regions = regionprops(b_labels)
    if len(regions) != 0:
        for region in regions:
            h, w = region.image.shape
            #Guardar región más grande que no sea desproporcionadamente alta o ancha
            if(region.area >= area_max) and (h * 10 > w and w * 10 > h):
                firma_slice = region.slice
                area_max = region.area
                firma = region.image
        #Si la imagen de la firma incluye el recuadro de la huella, eliminarlo
        if firma_slice[1].stop > 1800:
            firma=b_labels[int(firma_slice[0].start*0.99):int(firma_slice[0].stop*1.01),int(firma_slice[1].start*0.99):int(firma_slice[1].stop*0.8)]
        else: 
            firma=b_labels[int(firma_slice[0].start*0.99):int(firma_slice[0].stop*1.01),int(firma_slice[1].start*0.99):int(firma_slice[1].stop*1.01)]
        
        #Invertir color imagen y retornarla
        firma = firma.astype(np.uint8) * 255
        firma = reverse_color(firma)
        return firma
    #Retornar False si no se encuentran zonas de interés
    else: 
        return False

