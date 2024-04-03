import cv2
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from scipy.signal import argrelextrema

class multiAngle():
    def __init__(self, image:str, ref:str|np.ndarray) -> None:
        self.path = image
        if type(ref) == str:
            self.ref = cv2.imread(os.path.normpath(rf'{ref}'), cv2.IMREAD_GRAYSCALE)
        else:
            self.ref = ref

    def correction(self, image):
        mw = np.mean(self.ref)
        pic_cor = np.uint8((np.double(image) / np.double(self.ref)) * mw)
        return pic_cor
    
    def imageHandling(self) -> np.ndarray:
        image = cv2.imread(os.path.normpath(rf'{self.path}'), cv2.IMREAD_GRAYSCALE)
        pic_cor = self.correction(image)
        _, binary_image = cv2.threshold(pic_cor, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return binary_image
        
    def inv(self, binary_edit):
        inverted_image = cv2.bitwise_not(binary_edit)
        contours, _ = cv2.findContours(inverted_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            cv2.drawContours(binary_edit, [contour], 0, 0, -1)
        return binary_edit

if __name__ == '__main__':
    files = []
    path = r'H:\Duese_1\Wasser\2_60_68,3\Oben_fern'
    files = [x for x in os.listdir(path) if x.endswith('.png')]
    res = []
    ref = r'H:\Duese_1\Wasser\Oben_fern_ref.tif'
   
    prob_map = np.zeros_like(cv2.imread(os.path.normpath(rf'{ref}'), cv2.IMREAD_GRAYSCALE).astype(np.float32))
    for file in files:
        ma = multiAngle(os.path.join(path, file), ref)
        image = ma.imageHandling()
        
        plt.figure(figsize=(image.shape[1]/100.0, image.shape[0]/100.0), dpi=100) 
        plt.imshow(image, interpolation='nearest', cmap='Greys_r')
        
        plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)
        plt.xticks([])
        plt.yticks([])
        plt.tight_layout()
        plt.show()

        plt.figure(figsize=(image.shape[1]/100.0, image.shape[0]/100.0), dpi=100) 
        plt.imshow(ma.inv(image), interpolation='nearest', cmap='Greys_r')
        plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)
        plt.xticks([])
        plt.yticks([])
        plt.tight_layout()
        plt.show()
        pass
    

