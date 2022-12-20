import base64
import sys
import cv2
import numpy as np
from pdf2image import convert_from_bytes
from skimage import measure, morphology
from skimage.color import label2rgb
from skimage.measure import regionprops

import matplotlib.pyplot as plt

#with open("ci1.jpeg", "rb") as ci_file:
#    base64String = base64.b64encode(ci_file.read())

with open("CI.txt", "rb") as ci_file:
    base64String = ci_file.read()

ci_bytes = base64.b64decode(base64String)

nparr = np.frombuffer(ci_bytes, np.uint8)
image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#if image == None:
#    ci_images = convert_from_bytes(ci_bytes, dpi=300)
#    image = np.array(ci_images[2])

#image =  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

img = cv2.threshold(image, 160, 255, cv2.THRESH_BINARY)[1]

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
constant = average/img.shape[0]*img.shape[1]*7.75

b = morphology.remove_small_objects(blobs_labels, constant/5)
b = b.max() - b + b.min()

blobs_firma = b > b.mean()
b_labels = measure.label(blobs_firma, connectivity=2, background=1)

plt.figure(figsize=(10,10))

area_max = 0
for region in regionprops(b_labels):
    #print(region)
    plt.imshow(region.image,cmap='gray')
    plt.show()
    if(region.area >= area_max):
        firma_slice = region.slice
        area_max = region.area
        firma = region.image




