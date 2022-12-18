import base64
import sys
from pdf2image import convert_from_bytes
import cv2
import numpy as np
from skimage import measure, morphology
from skimage.color import label2rgb
from skimage.measure import regionprops

with open("pagare.pdf", "rb") as pdf_file:
    base64String = base64.b64encode(pdf_file.read())

pdf_bytes = base64.b64decode(base64String)

pdf_images = convert_from_bytes(pdf_bytes, dpi=300)
image = np.array(pdf_images[2])
image =  cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

img = cv2.threshold(image, 190, 255, cv2.THRESH_BINARY)[1]
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
constant = average/img.shape[0]*img.shape[1]*7.75

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

print(firma_slice)

