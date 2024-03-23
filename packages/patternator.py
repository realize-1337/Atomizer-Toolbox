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
    
    def calcAreas(self)->np.ndarray:
        delta = self.a+self.h
        colCenters = np.arange(0.5*self.h+0.5*self.a, 0.5*2*self.cols*delta, delta)
        print(colCenters)
        areas = np.zeros_like(colCenters)
        areas = np.pi*((colCenters+0.5*self.a)**2-(colCenters-0.5*self.a)**2)
        return(areas)
    
    def work_fit(self, areas, params):
        a, c, w = params
        liq = self.df['m_l'].to_numpy()[0]
        time = np.mean(self.df['time [s]'].to_numpy())
        dens = self.df['rho_l'].to_numpy()[0]
        x_data = np.arange(self.cols)
        arr = self.gaussian(x_data, *params)
        arr = self.lorentz(x_data, *params)

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
        print('Fitted:')
        print(f'Difference: {diff}\nRelative Difference: {diff/input*100}%')
    
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
            print(f'Difference: {diff}\nRelative Difference: {diff/input*100}%')

    def fit(self, centers):
        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        params = []
        integ = []
        x_data = np.arange(self.cols)
        for i in range(len(self.arr)):
            c = centers[i]
            left = self.arr[i, :int(c-0.5)][::-1]
            right = self.arr[i, int(c-0.5):]

            max = np.max(self.arr[i, :])
            max_point = np.argmax(self.arr[i, :])
            FWHM = abs(find_nearest(left, max/2) - find_nearest(right, max/2))

            popt, pcov = curve_fit(self.gaussian, xdata=x_data, ydata=self.arr[i, :], method='lm', p0=[max, x_data[max_point], FWHM], xtol=1e-9, gtol=1e-9)
            params.append([*popt])

            y, err = quad(self.gaussian, -np.inf, np.inf, args=(popt[0],popt[1],popt[2], ))
            integ.append(y)

        return [params, integ]
    
    def fit_lorentz(self, centers):
        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        params = []
        integ = []
        x_data = np.arange(self.cols)
        for i in range(len(self.arr)):
            c = centers[i]
            left = self.arr[i, :int(c-0.5)][::-1]
            right = self.arr[i, int(c-0.5):]

            max = np.max(self.arr[i, :])
            max_point = np.argmax(self.arr[i, :])
            FWHM = abs(find_nearest(left, max/2) - find_nearest(right, max/2))

            popt, pcov = curve_fit(self.lorentz, xdata=x_data, ydata=self.arr[i, :], method='lm', p0=[max, x_data[max_point], FWHM], xtol=1e-9, gtol=1e-9)
            params.append([*popt])

            y, err = quad(self.lorentz, -np.inf, np.inf, args=(popt[0],popt[1],popt[2], ))
            integ.append(y)

        return [params, integ]
    
    @staticmethod
    def gaussian(x, A, xc, w):
            return A*np.exp(-0.5*((x-xc)/w)**2)
    
    @staticmethod
    def lorentz(x, A, xc, w):
            return 2*A/np.pi*(w/(4*(x-xc)**2+w**2))
    


if __name__ == '__main__':
    pat = pat(r'C:\Users\david\Documents\Dev\Atomizer-Toolbox\test\patternator.xlsx')
    centers = pat.findCenter()
    areas = pat.calcAreas()
    
    pat.work(areas, centers)
    params, integ = pat.fit_lorentz(centers)
    time = pat.df['time [s]'].to_numpy()
    
    y_mean = 0
    a_mean = 0
    w_mean = 0
    for t, y, p in zip(time, integ, params):
        a, xc, w = p
        y_mean += t*y
        a_mean += t*a
        w_mean += t*w
    y_mean /= np.sum(time)
    a_mean /= np.sum(time)
    w_mean /= np.sum(time)

    p_inf = [a_mean, 55.6, w_mean]
    pat.work_fit(areas, p_inf)

    pass