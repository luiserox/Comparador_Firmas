import base64
import sys
from pdf2image import convert_from_bytes
import cv2
import numpy as np
from skimage import measure, morphology
from skimage.color import label2rgb
from skimage.measure import regionprops
from matplotlib import pyplot as plt

from base64__pdf import pdf_signature
from base64__ci import ci_signature
from recon_firma import region_firma

#Ruts de casos
ruts = ['13.237.661','7.394.171', '12.971.928', '10.304.793', '15.721.575', '15.057.662', '15.196.715', '10.474.004', '6.094.215', '12.522.921']

#Recorrer y leer los casos de CI y Pagaré
for i in range(1,11):
    with open("CIyPag/Caso{i}/{rut}/pag.txt".format(i=i,rut=ruts[i-1]), "rb") as pag_file:
        base64PDF = pag_file.read()
    
    with open("CIyPag/Caso{i}/{rut}/CI.txt".format(i=i,rut=ruts[i-1]), "rb") as ci_file:
        base64CI = ci_file.read()

    #Extraer firma de pdf
    firma_pdf = pdf_signature(base64PDF)

    #Extraer firma de CI
    firma_ci = ci_signature(base64CI)





