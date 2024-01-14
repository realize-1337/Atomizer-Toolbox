import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import plotly.express as px
from scipy.signal import argrelextrema

class multiAngle():
    def __init__(self, image:str, ref:str) -> None:
        self.path = image
        self.ref = cv2.imread(ref, cv2.IMREAD_GRAYSCALE)

    def correction(self, image):
        mw = np.mean(self.ref)
        pic_cor = np.uint8((np.double(image) / np.double(self.ref)) * mw)
        return pic_cor
    
    def imageHandling(self) -> np.ndarray:
        image = cv2.imread(self.path, cv2.IMREAD_GRAYSCALE)
        pic_cor = self.correction(image)
        _, binary_image = cv2.threshold(pic_cor, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return binary_image

        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        convex_hulls = [cv2.convexHull(cnt) for cnt in contours]
        solid_body = np.zeros_like(binary_image)
        cv2.fillPoly(solid_body, convex_hulls, 255)
        filled_black = np.zeros_like(binary_image)
        cv2.drawContours(filled_black, contours, -1, 255, thickness=cv2.FILLED)
        return filled_black
        

    def maxWidth(self,initialSkip=100) -> list:
        image = self.imageHandling()
        maxCount = 0
        maxCountRow = 0
        for i in range(initialSkip, len(image)):
            count = np.count_nonzero(image[i, :]==0)
            if count > maxCount:
                maxCount = count
                maxCountRow = i

        rows = np.arange(initialSkip, maxCountRow+1, (maxCountRow-initialSkip)/10)
        # print(rows)
        angles = []
        for row in rows:
            try:
                maxRow = image[int(row), :]
                xLeft = np.argmax(maxRow==0)
                xRight = np.argmax(maxRow[::-1]==0)

                width = len(maxRow)
                angle1 = np.tan(abs(xLeft-width/2)/row)
                angle2 = np.tan(abs(xRight-width/2)/row)
                angles.append(np.rad2deg(angle1)+np.rad2deg(angle2))
            except ZeroDivisionError:
                pass
        
        return [self.path, maxCount, maxCountRow, np.mean(angles)]


    def createList(self) -> tuple:
        return (float(np.count_nonzero(self.imageHandling()==0)), self.path)

    def show(self):
        image = self.imageHandling()
        # for row in range(len(image)):
        #     currow = image[int(row), :]
        #     xLeft = np.argmax(currow==0)
        #     xRight = np.argmax(currow[::-1]==0)
        #     image[int(row), xRight:xLeft] = 0
        edges = cv2.Canny(image, 0, 255)

        plt.imshow(edges)
        plt.show()

def handler(file, path=r'C:\Users\david\Desktop\Test PDA\Oben_fern', ref=r'C:\Users\david\Desktop\Test PDA\Oben_fern_ref.tif'):
    mA = multiAngle(os.path.join(path, file), ref)
    return mA.createList()

def handler2(file, ref=r'C:\Users\david\Desktop\Test PDA\Oben_fern_ref.tif'):
    try:
        mA = multiAngle(file, ref)
        return mA.maxWidth()
    except: return None

def handler3(file, ref=r'C:\Users\david\Desktop\Test PDA\Oben_fern_ref.tif'):
        try:
            mA = multiAngle(file, ref)
            return mA.imageHandling()
        except: return None

if __name__ == '__main__':
    files = []
    path = r'C:\Users\david\Desktop\Test PDA\Oben_fern'
    files = [x for x in os.listdir(path) if x.endswith('.png')]
    res = []
    ref = r'C:\Users\david\Desktop\Test PDA\Oben_fern_ref.tif'

    prob_map = np.zeros_like(cv2.imread(ref, cv2.IMREAD_GRAYSCALE).astype(np.float32))
    with Pool(16) as p, tqdm(total=len(files)) as pbar:
        for x in p.imap_unordered(handler3, [os.path.join(path, file) for file in files]):
            pbar.update(1)
            prob_map += (x == 0).astype(np.float32)

    prob_map /= len(files)    
    prob_map_scaled = (prob_map * 255).astype(np.uint8)
    # plt.imshow(prob_map_scaled)
    # plt.show()

    _, prob_bw = cv2.threshold(prob_map_scaled, 15, 255, cv2.THRESH_BINARY)

    y = np.zeros(len(prob_bw))
    # for i in range(len(prob_bw)-1, -1, -1):
    for i in range(len(prob_bw)):
        y[i] = np.sum(prob_bw[i, :] == 255)

    x = np.arange(0, len(y), 1)   
    diff = np.diff(y[:150], 1)
    p_ = np.poly1d(np.polyfit(x[:149], diff, 8))
    y_ = p_(x[:149])
    flm = argrelextrema(y_, np.less)[0][0]+5

    y = y[flm:]
    x = x[flm:]
    
    p = np.poly1d(np.polyfit(x, y, 8))
    diff = np.gradient(p(x))
    
    
    fig = px.line(p(x), markers=True)
    fig.show()
    fig = px.line(y_, markers=True)
    fig.show()
    fig = px.line(diff, markers=True)
    fig.show()

    y = p(x)

    max = np.argmax(y)
    end = np.argmax(y<=0)
    if end <= flm: end = len(y)-1

    print(max)
    print(end)
    print(p(max))

    angleMax = 0
    for i in range(end):
        ang = 2*np.rad2deg(np.arctan(0.5*(y[i]-y[0])/(i)))
        if ang > angleMax: 
            angleMax = ang
            pos = i
    
    angle10 = 2*np.rad2deg(np.arctan(0.5*(y[int(0.1*end)]-y[0])/(0.1*end)))
    angle50 = 2*np.rad2deg(np.arctan(0.5*(y[int(0.5*end)]-y[0])/(0.5*end)))
    angle90 = 2*np.rad2deg(np.arctan(0.5*(y[int(0.9*end)]-y[0])/(0.9*end)))

    print(f'Max: {angleMax} @ {pos}')
    print(f'10%: {angle10} @ {0.1*end}')
    print(f'50%: {angle50} @ {0.5*end}')
    print(f'90%: {angle90} @ {0.9*end}')

    half = int(len(prob_bw[0,:])/2)
    
    prob_map_scaled = cv2.line(prob_map_scaled, (int(half+0.5*y[0]),flm), (int(half+0.5*y[pos]), flm+pos), (255, 255, 255), 5)
    prob_map_scaled = cv2.line(prob_map_scaled, (int(half-0.5*y[0]),flm), (int(half-0.5*y[pos]), flm+pos), (255, 255, 255), 5)
    plt.imshow(prob_map_scaled)
    plt.show()

    
    print(1)

