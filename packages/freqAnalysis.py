import os
from skimage import io, color, filters, morphology, measure
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
import cv2


class freq():
    def __init__(self, refPath=None) -> None:
        self.ref = refPath
        if self.ref:
            self.refImage = cv2.imread(self.ref)

    def correction(self, image):
        if not self.ref: return
        mw = np.mean(self.refImage)
        print(mw)
        pic_cor = np.uint8(image.astype(float) / self.refImage.astype(float) * mw)
        print(f'Mean Value Corr: {np.mean(pic_cor)}')
        cv2.imshow('Pic Cor', pic_cor)
        cv2.waitKey()
        return pic_cor

    def read(self, path, x_start, x_end, y):
        # image = cv2.imread(path, cv2)
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        self.refImage = cv2.cvtColor(self.refImage, cv2.COLOR_BGR2GRAY)
        pic_cor = self.correction(image)
        # gray = cv2.cvtColor(pic_cor, cv2.COLOR_BGR2GRAY)
        # binary_raw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        _, binary_image = cv2.threshold(pic_cor, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        minPix = np.count_nonzero(binary_image == 0)/2
        print(minPix)
        binary_edit = morphology.remove_small_objects(binary_image, min_size=round(minPix))
        inverted_image = cv2.bitwise_not(binary_edit)

        contours, _ = cv2.findContours(inverted_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            cv2.drawContours(binary_edit, [contour], 0, 0, -1)  # Fill with black color

        line = binary_edit[y, x_start:x_end]
        
        cv2.imshow('Debug', binary_edit)
        cv2.waitKey()


        return np.sum(line)

    def readSKI(self, path, x_start, x_end, y):
        image = io.imread(path)
        pic_cor = self.correction(image)
        gray = color.rgb2gray(pic_cor)
        level = filters.threshold_otsu(gray)
        print(level)
        binary_image = gray > level


        io.imshow(binary_image)
        plt.show()
        
    def newRead(self, path, x_start, x_end, y):
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        self.refImage = cv2.cvtColor(self.refImage, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(image, self.refImage)
        # cv2.imshow('Droplets', diff)
        # cv2.waitKey(0)
        _, binary = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        droplets_extracted = cv2.bitwise_and(image, image, mask=binary)

        minPix = np.count_nonzero(binary == 0)/2
        print(minPix)
        binary_edit = morphology.remove_small_objects(binary, min_size=round(minPix))

        cv2.imshow('Droplets', binary_edit)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run(self, path):
        self.read(path, 600, 1400, 200)
        # self.readSKI(path, 600, 1400, 200)
        # self.newRead(path, 600, 1400, 200)



if __name__ == '__main__':
    freq_ = freq(r'M:\Duese_3\Wasser\Oben_fern_ref.tif')
    freq_.run(r'M:\Duese_3\Wasser\2,5_56,4_45\Oben_fern\frame_0000.png')

    # # freq.multi(r'C:\Users\david\Desktop\1_4,4_17,2\Oben_fern', '.png')
    # path = r'C:\Users\david\Desktop\1_4,4_17,2\Oben_fern'
    # type = '.png'
    # files = [os.path.join(path, x) for x in os.listdir(path) if x.endswith(type)]
    # files.sort()
    # # print(len(files))
    # # print(files)
    # i = 0
    # # 
    # with Pool(12) as p:
    #     results = p.map(freq_.read, files)
    
    # print(results)
