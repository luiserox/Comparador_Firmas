import base64
import sys
import cv2
import numpy as np
from pdf2image import convert_from_bytes
from skimage import measure, morphology
from skimage.color import label2rgb
from skimage.measure import regionprops

from signature_detect.loader import Loader
from signature_detect.extractor import Extractor
from signature_detect.cropper import Cropper
from signature_detect.judger import Judger

import matplotlib.pyplot as plt

def reverse_color(img):
  return img.max() - img + img.min()

def show_image(img):
    fig, ax = plt.subplots(figsize=(5, 10))
    ax.imshow(img, cmap = 'gray')
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()

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

    thresh = cv2.adaptiveThreshold(blurred, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 2)

    img = thresh

    amplfier = 30
    extractor = Extractor(amplfier=amplfier, min_area_size=10)
    labeled_mask = extractor.extract(thresh)


    plt.figure(figsize=(10,10))
    plt.imshow(labeled_mask,cmap='gray')
    plt.show()

    b = labeled_mask
    blobs_firma = b > b.mean()
    b_labels = measure.label(blobs_firma, connectivity=2, background=1)
    area_max = 0

    for region in regionprops(b_labels):
        h, w = region.image.shape
        if(region.area >= area_max) and (h * 10 > w and w * 10 > h):
            firma_slice = region.slice
            area_max = region.area
            firma = region.image

    #firma=labeled_mask[firma_slice[0].start:int(firma_slice[0].stop * 1.1),int(firma_slice[1].start * 0.8):int(firma_slice[1].stop*0.8)]
    firma = reverse_color(firma.astype(np.uint8) * 255)

    return firma

with open("CI.txt", "rb") as ci_file:
        base64CI = ci_file.read()

firma = ci_signature(base64CI)

print(firma.mean())