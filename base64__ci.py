import base64
import sys
import cv2
import numpy as np
from pdf2image import convert_from_bytes
from skimage import measure, morphology
from skimage.color import label2rgb
from skimage.measure import regionprops

import matplotlib.pyplot as plt

def reverse_color(img):
  return img.max() - img + img.min()

def ci_signature(base64CI):

    ci_bytes = base64.b64decode(base64CI)

    nparr = np.frombuffer(ci_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        ci_images = convert_from_bytes(ci_bytes, dpi=300)
        image = np.array(ci_images[0])

    #image =  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    thresh = cv2.adaptiveThreshold(blurred, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 7, 5)

    img = thresh
    img = reverse_color(img)
    parametro = 0.5

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

    blobs_firma = b > b.mean()
    b_labels = measure.label(blobs_firma, connectivity=2, background=1)

    area_max = 0
    for region in regionprops(b_labels):
        if(region.area >= area_max):
            firma_slice = region.slice
            area_max = region.area
            firma = region.image

    return firma




