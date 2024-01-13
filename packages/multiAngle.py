import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import morphology
import os
import pandas as pd

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

        maxRow = image[i, :]
        xLeft = np.argmax(maxRow==0)
        xRight = np.argmax(maxRow[::-1]==0)

        print(f'File: {self.path}')
        print(f'y pos = {i}')
        print(f'xLeft = {xLeft}, xRight = {xRight}')
        width = len(maxRow)
        angle1 = np.tan(abs(xLeft-width/2)/i)
        angle2 = np.tan(abs(xRight-width/2)/i)
        print(f'Left Half angle: {np.rad2deg(angle1)} - Right Half angle: {np.rad2deg(angle2)}')
        print('--'*20)

        return [self.path, maxCount, maxCountRow]


    def createList(self) -> tuple:
        return (float(np.count_nonzero(self.imageHandling()==0)), self.path)

    def show(self):
        plt.imshow(self.imageHandling())
        plt.show()

if __name__ == '__main__':
    files = []
    path = r'C:\Users\david\Desktop\Duese_1\4,1_7,5_70\Oben_fern'
    files = os.listdir(path)
    res = []
    ref = r'C:\Users\david\Desktop\Duese_1\Oben_fern_ref.tif'

    for i,file in enumerate(files):
        print(i)
        # if i == 10: break
        mA = multiAngle(os.path.join(path, file), ref)
        res.append(mA.createList())

    df = pd.DataFrame(res, columns=['Count', 'File'])
    df = df.sort_values('Count', ascending=False).reset_index()

    max = []
    for index, row in df.iterrows():
        if index == 15: break
        mA = multiAngle(row['File'], ref)
        max.append(mA.maxWidth())
    
    maxdf = pd.DataFrame(max, columns=['File', 'Count', 'Row'])
    maxdf = maxdf.sort_values('Count', ascending=False).reset_index()

    for index, row in maxdf.iterrows():
        mA = multiAngle(row['File'], ref)
        mA.show()

    
    print(1)

