import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import curve_fit
from scipy.integrate import quad


class pat():
    def __init__(self, path, a=5.5, b=5.5, h=0.35 ) -> None:
        self.path = path
        self.a = a
        self.b = b
        self.h = h

    def read(self)-> np.ndarray:
        self.df = pd.read_excel(self.path, decimal=',')
        self.df = self.df.fillna(0)
        arr = self.df.to_numpy()[:,7:]
        self.cols = len(arr[0, :])
        self.arr = arr.astype(np.float32)
    
    def findCenter(self)->list:
        self.read()
        max = np.argmax(self.arr, axis=1)
        max_2 = []
        for i, m in enumerate(max):
            off = (np.argmax(self.arr[i, m-1:m+2:1]))
            if off == 1: 
                max_2.append(m+1)
            else: max_2.append(m-1)
        center = []
        for m1, m2 in zip(max, max_2):
            center.append(0.5*(m1+m2))
        return center
    
    def calcAreas(self, centers:list)->np.ndarray:
        delta = self.a+self.h
        colCenters = np.arange(0.5*self.h+0.5*self.a, 0.5*2*self.cols*delta, delta)
        print(colCenters)
        areas = np.zeros_like(colCenters)
        areas = np.pi*((colCenters+0.5*self.a)**2-(colCenters-0.5*self.a)**2)
        factor = areas/(self.a*self.b)/2
        fig = px.line(factor)
        fig.show()
        return(areas)
    
    def work(self, areas, centers):
        liq = self.df['m_l'].to_numpy()
        time = self.df['time [s]'].to_numpy()
        dens = self.df['rho_l'].to_numpy()
        for i, c in enumerate(centers):
            left = self.arr[i, :int(c-0.5)][::-1]
            right = self.arr[i, int(c-0.5):]
            factor = areas/(self.a*self.b)/2
            
            # this are the volumes of liquid in each ring [m**3]
            volLeft = left*self.a*self.b*factor[:len(left)]*1e-9
            volRight = right*self.a*self.b*factor[:len(right)]*1e-9

            if dens[i] == 1236.27:
                volLeft = volLeft*(1-0.0431)
                volRight = volRight*(1-0.0431)
            if dens[i] == 1222.96:
                volLeft = volLeft*(1-0.0163)
                volRight = volRight*(1-0.0163)
            

            total = np.sum(np.concatenate((volLeft, volRight)))
            input = liq[i]/3600*time[i]/dens[i]
            diff = input-total
            print(f'Difference: {diff} \n Relative Difference: {diff/input*100}%')

    def fit(self, centers):
        def gaussian(x, A, xc, w):
            return A*np.exp(-0.5*((x-xc)/w)**2)
        
        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        params = []
        integ = []
        # delta = self.a+self.h
        # x_data = np.arange(self.h+0.5*self.a, self.cols*delta, delta)
        x_data = np.arange(self.cols)
        time = self.df['time [s]'].to_numpy()
        for i in range(len(self.arr)):
            c = centers[i]
            left = self.arr[i, :int(c-0.5)][::-1]
            right = self.arr[i, int(c-0.5):]

            max = np.max(self.arr[i, :])
            max_point = np.argmax(self.arr[i, :])
            FWHM = abs(find_nearest(left, max/2) - find_nearest(right, max/2))

            popt, pcov = curve_fit(gaussian, xdata=x_data, ydata=self.arr[i, :], method='lm', p0=[max, x_data[max_point], FWHM], xtol=1e-9, gtol=1e-9)
            params.append([*popt])

            y, err = quad(gaussian, -np.inf, np.inf, args=(popt[0],popt[1],popt[2], ))
            integ.append(y/time[i])

        return [params, integ]

    def workWithFit(self, areas, A, w, c=56.5):
        liq = self.df['m_l'].to_numpy()[0]
        time = np.mean(self.df['time [s]'].to_numpy())
        dens = self.df['rho_l'].to_numpy()[0]

        def gaussian(x, A, xc, w):
            return A*np.exp(-0.5*((x-xc)/w)**2)

        x_data = np.arange(self.cols)
        arr = gaussian(x_data, A, c, w)

        left = arr[:int(c-0.5)][::-1]
        right = arr[int(c-0.5):]
        factor = areas/(self.a*self.b)/2
        
        # this are the volumes of liquid in each ring [m**3]
        volLeft = left*self.a*self.b*factor[:len(left)]*1e-9
        volRight = right*self.a*self.b*factor[:len(right)]*1e-9

        if dens == 1236.27:
            volLeft = volLeft*(1-0.0431)
            volRight = volRight*(1-0.0431)
        if dens == 1222.96:
            volLeft = volLeft*(1-0.0163)
            volRight = volRight*(1-0.0163)
        

        total = np.sum(np.concatenate((volLeft, volRight)))
        input = liq/3600*time/dens
        diff = input-total
        print(f'Difference: {diff} \n Relative Difference: {diff/input*100}%')

if __name__ == '__main__':
    pat = pat(r'C:\Users\david\Documents\Dev\Atomizer-Toolbox\test\patternator.xlsx')
    centers = pat.findCenter()
    areas = pat.calcAreas(centers)

    print(areas)
    fig = px.line(areas)
    fig.show()

    pat.work(areas, centers)
    params, integ = pat.fit(centers)

    a_mean = 0
    w_mean = 0
    for A, xc, w in params:
        a_mean += A
        w_mean += w
    a_mean /= len(params)
    w_mean /= len(params)
    print(params)
    print(integ)

    pat.workWithFit(areas, a_mean, w_mean)
    pass