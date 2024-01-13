import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import plotly.express as px

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

if __name__ == '__main__':
    files = []
    path = r'C:\Users\david\Desktop\Test PDA\Oben_fern'
    files = [x for x in os.listdir(path) if x.endswith('.png')]
    res = []
    ref = r'C:\Users\david\Desktop\Test PDA\Oben_fern_ref.tif'

    with Pool(16) as p, tqdm(total=len(files)) as pbar:
        for x in p.imap_unordered(handler, files):
            pbar.update(1)
            res.append(x)

    df = pd.DataFrame(res, columns=['Count', 'File'])
    df = df.sort_values('Count', ascending=False).reset_index()

    max = []
    rows = []
    for index, row in df.iterrows():
        if index == 20: break
        # mA = multiAngle(row['File'], ref)
        # max.append(mA.maxWidth())
        rows.append(row['File'])

    with Pool(16) as p, tqdm(total=len(files)) as pbar:
        for x in p.imap_unordered(handler2, rows):
            pbar.update(1)
            if not x == None:
                max.append(x)
    
    maxdf = pd.DataFrame(max, columns=['File', 'Count', 'Row', 'Angle'])
    maxdf = maxdf.sort_values('Count', ascending=False).reset_index()

    print(f"Mean: {maxdf['Angle'].mean()}")
    print(f"Std: {maxdf['Angle'].std(ddof=0)}")


    for index, row in maxdf.iterrows():
        mA = multiAngle(row['File'], ref)
        mA.show()

    fig = px.line(maxdf['Angle'], labels={'0':'Hozizontal Position [mm]',
                                          'value':'D32 [µm]'}, markers=True)
    fig.show()
    print(1)

