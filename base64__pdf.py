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

def reverse_color(img):
  return img.max() - img + img.min()

def pdf_signature(base64PDF):

    pdf_bytes = base64.b64decode(base64PDF)

    pdf_images = convert_from_bytes(pdf_bytes, dpi=300)
    image = np.array(pdf_images[2])
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    thresh = cv2.adaptiveThreshold(blurred, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 7, 5)

    img = thresh
    img = reverse_color(img)
    parametro = 0.4

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
    constant = average/img.shape[0]*img.shape[1] * 7.75 * parametro

    b = morphology.remove_small_objects(blobs_labels, constant)
    b = b.max() - b + b.min()

    plt.figure(figsize=(10,10))
    plt.imshow(b,cmap='gray')
    plt.show()

    blobs_firma = b > b.mean()
    b_labels = measure.label(blobs_firma, connectivity=2, background=1)

    area_max = 0
    regions = regionprops(b_labels)
    if len(regions) != 0:
        for region in regions:
            h, w = region.image.shape
            if(region.area >= area_max) and (h * 10 > w and w * 10 > h):
                firma_slice = region.slice
                area_max = region.area
                firma = region.image
        if firma_slice[1].stop > 1800:
            firma=b_labels[int(firma_slice[0].start*0.99):int(firma_slice[0].stop*1.01),int(firma_slice[1].start*0.99):int(firma_slice[1].stop*0.8)]
        else: 
            firma=b_labels[int(firma_slice[0].start*0.99):int(firma_slice[0].stop*1.01),int(firma_slice[1].start*0.99):int(firma_slice[1].stop*1.01)]
        
        firma = firma.astype(np.uint8) * 255
        firma = reverse_color(firma)
        return firma
    else: 
        return False

