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

class SprayAnglePP():
    def __init__(self) -> None:
        pass

    def findWidth(self, image:np.ndarray) -> list:
        c = int(len(image[0, :])/2)

        left = np.zeros(len(image[:, 0]))
        right = np.zeros_like(left)

        for row in range(len(left)):
            for i in range(c, -1, -1):
                if image[row, i] == 255: left[row] += 1
                else: break
            for i in range(c+1, len(image[:, 0])-1):
                if image[row, i] == 255: right[row] += 1
                else: break
            
        return [left, right]

    def calculateAngles(self, arr:list|np.ndarray, maxLenForFLM=150, flmSkip=20, maxAngleSkip=10, widget=None) -> list:
        if type(arr) != list:
            arr = [arr]
        
        trigger = False
        if widget.leftPoint and widget.rightPoint:
            trigger = True
            flm_preset = [widget.leftPoint, widget.rightPoint]

        flm = np.zeros(2, dtype=np.uint16)
        angles = np.zeros((4, 2))
        pos = np.zeros((4, 2), dtype=np.uint16)
        # print(arr)
        # print('RUN ANGLE')
        for num, y in enumerate(arr):
            x = np.arange(0, len(y), 1)   
            diff = np.diff(y[:maxLenForFLM], 1)
            p_ = np.poly1d(np.polyfit(x[:maxLenForFLM-1], diff, 8))
            y_ = p_(x[:maxLenForFLM-1])
            if not trigger:
                flm[num] = argrelextrema(y_, np.less)[0][0]+flmSkip
            else: flm[num] = int(flm_preset[num][1])

            y = y[flm[num]:]
            x = x[flm[num]:]
            p = np.poly1d(np.polyfit(x, y, 8))
            y = p(x)
            
            if trigger: y[0] = 0.5*abs(flm_preset[0][0]-flm_preset[1][0])
            end = np.argmax(y<=0)
            if end <= flm[num]: end = len(y)-1

            angleMean = np.zeros_like(x)   
            angleMean = np.rad2deg(np.arctan((y-y[0])/(x)))

            angles[0, num] = np.mean(angleMean[:end])
            angles[1, num] = np.rad2deg(np.arctan((y[int(0.1*end)]-y[0])/(0.1*end)))
            angles[2, num] = np.rad2deg(np.arctan((y[int(0.5*end)]-y[0])/(0.5*end)))
            angles[3, num] = np.rad2deg(np.arctan((y[int(0.9*end)]-y[0])/(0.9*end)))

            print(f'Mean angle: {angles[0, num]}')
        return [np.sum(angles, axis=1), pos, flm]
    
    def calculateAnglesMaxWidth(self, arr:list|np.ndarray, maxLenForFLM=150, flmSkip=20, maxAngleSkip=10, widget=None) -> list:
        if type(arr) != list:
            arr = [arr]

        trigger = False
        if widget.leftPoint and widget.rightPoint:
            trigger = True
            flm_preset = [widget.leftPoint, widget.rightPoint]

        flm = np.zeros(2, dtype=np.uint16)
        angles = np.zeros((4, 2))
        pos = np.zeros((4, 2), dtype=np.uint16)
        # print(arr)
        # print('RUN ANGLE')
        for num, y in enumerate(arr):
            x = np.arange(0, len(y), 1)              
            diff = np.diff(y[:maxLenForFLM], 1)
            p_ = np.poly1d(np.polyfit(x[:maxLenForFLM-1], diff, 8))
            y_ = p_(x[:maxLenForFLM-1])
            if not trigger:
                flm[num] = argrelextrema(y_, np.less)[0][0]+flmSkip
            else: flm[num] = int(flm_preset[num][1])

            y = y[flm[num]:]
            x = x[flm[num]:]
            p = np.poly1d(np.polyfit(x, y, 8))
            y = p(x)
            if trigger: y[0] = 0.5*abs(flm_preset[0][0]-flm_preset[1][0])

            angleTest = np.zeros_like(x)   
            angleTest = np.rad2deg(np.arctan((y-y[0])/(x)))
            
            end = np.argmax(y<=0)
            if end <= flm[num]: end = len(y)-1

            angleMax = 0
            maxPoint = np.argmax(y[maxAngleSkip:])
            angleMax = np.rad2deg(np.arctan((y[maxPoint]-y[0])/(maxPoint)))

            angles[0, num] = angleMax
            angles[1, num] = np.rad2deg(np.arctan((y[int(0.1*end)]-y[0])/(0.1*end)))
            angles[2, num] = np.rad2deg(np.arctan((y[int(0.5*end)]-y[0])/(0.5*end)))
            angles[3, num] = np.rad2deg(np.arctan((y[int(0.9*end)]-y[0])/(0.9*end)))
            
            # try: pos[0, num] = pos_
            # except: pos[0, num] = None
            # pos[1, num] = int(0.1*end)
            # pos[2, num] = int(0.5*end)
            # pos[3, num] = int(0.9*end)
        
        return [np.sum(angles, axis=1), pos, flm]

    def createImages(self, right, left, flm:np.ndarray, angles:np.ndarray, prob_map_scaled, widget=None, drawNegative=False, draw:list=[True, True, True, True]) -> list:
        '''
        Returns heatmap and heatmap with angles
        '''
        half = int(len(prob_map_scaled[0,:])/2)

        if widget == None:
            fig, ax = plt.subplots()
        else:
            fig = widget.figure
            ax = widget.ax
            ax.clear()
        heatmap = ax.imshow(prob_map_scaled/255*100, cmap='gist_heat_r')
        colors = 'blue', 'green', 'yellow', 'purple'

        trigger = False
        if widget.leftPoint and widget.rightPoint:
            trigger = True
            flm_preset = [widget.leftPoint, widget.rightPoint]

        if not len(fig.axes) > 1:
            fig.colorbar(heatmap, format='%d%%', label='Percentage of Spray Coverage')
        for row, color in enumerate(colors):
            if draw[row] == False: continue
            if trigger:
                point1 = flm_preset[1]
                point3 = flm_preset[0]
            else:
                point1 = (int(half+right[flm[0]]),flm[0])
                point3 = (int(half-left[flm[1]]),flm[1])

            slopeL = np.tan(np.deg2rad(-90-0.5*angles[row]))
            slopeR = np.tan(np.deg2rad(-90+0.5*angles[row]))

            image_size = np.shape(prob_map_scaled)
            extended_point1 = (0, int(point1[1] - slopeL * point1[0]))
            extended_point2 = (image_size[1], int(point1[1] + slopeL * (image_size[1] - point1[0])))
            extended_point3 = (0, int(point3[1] - slopeR * point3[0]))
            extended_point4 = (image_size[1], int(point3[1] + slopeR * (image_size[1] - point3[0])))

            try:
                ax.axline(extended_point1, extended_point2, color=color, linewidth=1)
                ax.axline(extended_point3, extended_point4, color=color, linewidth=1)
            except: 
                pass
        
        # ax.set_aspect('equal')
        size = np.shape(prob_map_scaled)
        ax.set_xlim(0, size[1])
        ax.set_ylim(size[0], 0)

        fig2, ax2 = plt.subplots()
        heatmap = ax2.imshow(prob_map_scaled, cmap='gist_heat_r')
        size = np.shape(prob_map_scaled)
        ax2.set_xlim(0, size[1])
        ax2.set_ylim(size[0], 0)

        return [fig, ax, fig2, ax2]
    
    def run(self, binary_map:np.ndarray, scaled_map:np.ndarray, widget, flmSkip=20, maxLenForFLM=150, drawNegative=True, draw:list=[True, True, True, True], maxAngleSkip=10, mode='maxW') -> list:
        '''
        Handles the post processing of spray angle calculation.
        Returns found angles, heatmap image and heatmap image with spray angles.
        Angles are max, 10, 50, 90.
        '''
        r, l = self.findWidth(binary_map)
        print(f'Left Preset Point: {widget.leftPoint}')
        print(f'Right Preset Point: {widget.rightPoint}')
        if mode == 'maxW':
            angles, pos, flm = self.calculateAnglesMaxWidth([r, l], maxLenForFLM, flmSkip, maxAngleSkip, widget)
        else:
            angles, pos, flm = self.calculateAngles([r, l], maxLenForFLM, flmSkip, maxAngleSkip, widget)
        fig, ax, figRaw, axRaw = self.createImages(r, l, flm, angles, scaled_map, widget, drawNegative, draw)

        return([angles, (fig, ax), (figRaw, axRaw)])


def initializeProbMap(raw:np.ndarray|str) -> np.ndarray:
    try:
        if type(raw) == str:
            return np.zeros_like(cv2.imread(os.path.normpath(rf'{ref}'), cv2.IMREAD_GRAYSCALE), dtype=np.float32)
        else: 
            return np.zeros_like(raw, dtype=np.float32)
    except: raise ValueError

def sumProbMap(sum:np.ndarray, image:np.ndarray) -> np.ndarray:
    # try:
    sum += (image == 0).astype(np.float32)
    return sum
    # except: raise IndexError

def createProbMap(prob_map:np.ndarray, num:float|int, threshold=10) -> list:
    '''
    Return binaray Prob_Map and scaled Prob_Map
    '''
    prob_map_uni = prob_map / num     
    prob_map_scaled = (prob_map_uni * 255).astype(np.uint8)

    _, prob_bw = cv2.threshold(prob_map_scaled, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(prob_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled_image = np.zeros_like(prob_bw)
    cv2.drawContours(filled_image, contours, -1, (255), thickness=cv2.FILLED)
    prob_bw = filled_image

    return [prob_bw, prob_map_scaled]

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
   
    prob_map = np.zeros_like(cv2.imread(os.path.normpath(rf'{ref}'), cv2.IMREAD_GRAYSCALE).astype(np.float32))
    with Pool(16) as p, tqdm(total=len(files)) as pbar:
        for x in p.imap_unordered(handler3, [os.path.join(path, file) for file in files]):
            pbar.update(1)
            prob_map += (x == 0).astype(np.float32)

    prob_map /= len(files)    
    prob_map_scaled = (prob_map * 255).astype(np.uint8)
    # plt.imshow(prob_map_scaled)
    # plt.show()

    _, prob_bw = cv2.threshold(prob_map_scaled, 10, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(prob_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled_image = np.zeros_like(prob_bw)
    cv2.drawContours(filled_image, contours, -1, (255), thickness=cv2.FILLED)
    prob_bw = filled_image

    test = SprayAnglePP()
    left, right = test.findWidth(prob_bw)
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=np.arange(len(left)), y=left, mode='lines', name='Left'))
    # fig.add_trace(go.Scatter(x=np.arange(len(right)), y=right, mode='lines', name='Right'))
    # fig.update_layout(title='Line Plot of Two 1D Numpy Arrays',
    #               xaxis_title='Index',
    #               yaxis_title='Values')
    # fig.show()


    flm_max = 0
    flm = np.zeros(2, dtype=np.uint16)
    # flm = np.array([30, 30])
    fits = []
    angles = np.zeros((4, 2))
    pos = np.zeros((4, 2), dtype=np.uint16)
    for num, y in enumerate([right, left]):
        x = np.arange(0, len(y), 1)   
        diff = np.diff(y[:150], 1)
        p_ = np.poly1d(np.polyfit(x[:149], diff, 8))
        y_ = p_(x[:149])
        # fig = px.line(y_, markers=True)
        # fig.show()
        flm[num] = argrelextrema(y_, np.less)[0][0]+20

        y = y[flm[num]:]
        x = x[flm[num]:]
        p = np.poly1d(np.polyfit(x, y, 8))
        fits.append(p)
        y = p(x)

        max = np.argmax(y)
        end = np.argmax(y<=0)
        if end <= flm[num]: end = len(y)-1

        angleMax = 0
        for i in range(10, end):
            ang = np.rad2deg(np.arctan((y[i]-y[0])/(i)))
            if ang > angleMax: 
                angleMax = ang
                pos_ = i

        angles[0, num] = angleMax
        angles[1, num] = np.rad2deg(np.arctan((y[int(0.1*end)]-y[0])/(0.1*end)))
        angles[2, num] = np.rad2deg(np.arctan((y[int(0.5*end)]-y[0])/(0.5*end)))
        angles[3, num] = np.rad2deg(np.arctan((y[int(0.9*end)]-y[0])/(0.9*end)))
        pos[0, num] = pos_
        pos[1, num] = int(0.1*end)
        pos[2, num] = int(0.5*end)
        pos[3, num] = int(0.9*end)

    angles = np.sum(angles, axis=1)
   
    half = int(len(prob_bw[0,:])/2)

    # print(angles)

    fig, ax = plt.subplots()
    heatmap = ax.imshow(prob_map_scaled, cmap='gist_heat_r')
    colors = 'blue', 'green', 'yellow', 'purple'
    for row, color in enumerate(colors):
        point1 = (int(half+right[flm[0]]),flm[0])
        point3 = (int(half-left[flm[1]]),flm[1])

        slopeL = np.tan(np.deg2rad(-90-0.5*angles[row]))
        slopeR = np.tan(np.deg2rad(-90+0.5*angles[row]))

        image_size = np.shape(prob_map_scaled)
        extended_point1 = (0, int(point1[1] - slopeL * point1[0]))
        extended_point2 = (image_size[1], int(point1[1] + slopeL * (image_size[1] - point1[0])))
        extended_point3 = (0, int(point3[1] - slopeR * point3[0]))
        extended_point4 = (image_size[1], int(point3[1] + slopeR * (image_size[1] - point3[0])))

        ax.axline(extended_point1, extended_point2, color=color, linewidth=1)
        ax.axline(extended_point3, extended_point4, color=color, linewidth=1)

        # prob_map_scaled = cv2.line(prob_map_scaled, extended_point1, extended_point2, (255, 255, 255), 5)
        # prob_map_scaled = cv2.line(prob_map_scaled, extended_point3, extended_point4, (255, 255, 255), 5)
    # plt.imshow(prob_map_scaled, cmap='hot_r')
    ax.set_aspect('equal')
    size = np.shape(prob_map_scaled)
    ax.set_xlim(0, size[1])
    ax.set_ylim(size[0], 0)

    plt.show()

    
    print(1)

