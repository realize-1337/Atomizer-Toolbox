import os
from skimage import io, color, filters, morphology, measure
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool


class freq():
    def __init__(self, refPath=None) -> None:
        self.ref = refPath
        if self.ref:
            self.refImage = io.imread(self.ref)

    def correction(self, image):
        if not self.ref: return
        mw = np.mean(image)
        # print(image)
        pic_cor = image.astype(float)/self.refImage.astype(float) * mw

        return np.uint8(pic_cor)

    def read(self, path, x_start, x_end, y):
        image = io.imread(path)
        self.correction(image)
        gray = color.rgb2gray(image)

        threshold = filters.threshold_otsu(gray)
        binary = gray <= threshold

        black_pixel_count = len(binary[binary == 0])
        min_pix = black_pixel_count / 2

        binary_edit = morphology.remove_small_objects(binary, min_size=round(min_pix))

        line = binary_edit[y, x_start:x_end]

        return np.sum(line)


    def run(self, path):
        self.read(path)



if __name__ == '__main__':
    freq_ = freq(r'J:\Duese_1\Oben_fern_ref.tif')
    freq_.run(r'C:\Users\david\Desktop\1_4,4_17,2\Oben_fern\frame_0070.png')

    # freq.multi(r'C:\Users\david\Desktop\1_4,4_17,2\Oben_fern', '.png')
    path = r'C:\Users\david\Desktop\1_4,4_17,2\Oben_fern'
    type = '.png'
    files = [os.path.join(path, x) for x in os.listdir(path) if x.endswith(type)]
    files.sort()
    # print(len(files))
    # print(files)
    i = 0
    # 
    with Pool(12) as p:
        results = p.map(freq_.read, files)
    
    print(results)
