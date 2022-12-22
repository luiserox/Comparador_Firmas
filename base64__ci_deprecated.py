import base64
import sys
import cv2
import numpy as np
from pdf2image import convert_from_bytes
from skimage import measure, morphology
from skimage.color import label2rgb
from skimage.measure import regionprops

import matplotlib.pyplot as plt
from recon_firma import region_firma

def reverse_color(img):
  return img.max() - img + img.min()

def show_image(img):
    fig, ax = plt.subplots(figsize=(5, 10))
    ax.imshow(img, cmap = 'gray')
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()

def ci_signature(base64CI):

    image = region_firma(base64CI)

    if image is False:
        return False
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    thresh = cv2.adaptiveThreshold(blurred, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 7, 2)

    img = thresh
    img = reverse_color(img)
    parametro = 0.3

    plt.figure(figsize=(10,10))
    plt.imshow(img,cmap='gray')
    plt.show()

    blobs = img > img.mean()
    blobs_labels = measure.label(blobs, background=1)
    image_label_overlay = label2rgb(blobs_labels, image=img)

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
                
    average = (total_area/counter)            
    constant = average/img.shape[0]*img.shape[1]*7.75*parametro

    b = morphology.remove_small_objects(blobs_labels, constant)
    b = b.max() - b + b.min()

    show_image(b)

    blobs_firma = b > b.mean()
    b_labels = measure.label(blobs_firma, connectivity=2, background=1)

    max_area = 0
    for region in regionprops(b_labels):
        if(region.area >= max_area):
            show_image(region.image)
            firma_slice = region.slice
            max_area = region.area
            firma = region.image

    if max_area != 0:
        firma = reverse_color(firma.astype(np.uint8) * 255)
        return firma
    else:
        return False

ruts = ['13.237.661','7.394.171', '12.971.928', '10.304.793', '15.721.575', '15.057.662', '15.196.715', '10.474.004', '6.094.215', '12.522.921']

for i in range(1,11):

    with open("CIyPag/Caso{i}/{rut}/CI.txt".format(i=i,rut=ruts[i-1]), "rb") as ci_file:
        base64CI = ci_file.read()
    
    firma = ci_signature(base64CI)
    if firma is not False:
        show_image(firma)


