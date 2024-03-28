import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.optimize import curve_fit
from scipy.integrate import quad
from sklearn.metrics import r2_score


class pat():
    def __init__(self, path, a=5.5, b=5.5, h=0.35 ) -> None:
        self.path = path
        self.a = a
        self.b = b
        self.h = h
        self.current_it = 0
        self.globalread()

    def globalread(self)->None:
        self.gdf = pd.read_excel(self.path, decimal=',')
        self.exportDF = self.gdf.copy().iloc[:,0:7]
        self.exportDF['Width[mm]'] = np.nan
        self.exportDF['exDelta'] = np.nan
        self.exportDF['fitDelta'] = np.nan
        self.exportDF['Fit-R2'] = np.nan
        self.exportDF['exPDA'] = np.nan
        self.exportDF['fitPDA'] = np.nan
        self.it = len(self.gdf)/3
        self.gdf = self.gdf.fillna(0)
        self.gdf = self.gdf.applymap(lambda x: 0 if isinstance(x, str) and x.strip() == '' else x)
        arr = self.gdf.to_numpy()[:,7:]
        self.gcols = len(arr[0, :])
        self.garr = arr#.astype(np.float32)

    def read(self)-> None:
        self.df = self.gdf.iloc[self.current_it:self.current_it+3]
        # print(self.df)
        print(25*'--')
        print(f"{self.df['s_l'][self.current_it]} - {self.df['m_g,i'][self.current_it]} - {self.df['m_l'][self.current_it]} - {self.df['m_g,o'][self.current_it]} - {self.df['rho_l'][self.current_it]}")
        self.current_it += 3
        arr = self.df.to_numpy()[:,7:]
        self.cols = len(arr[0, :])
        self.arr = arr.astype(np.float32)
        
    def findCenter(self)->list:
        self.read()
        max = np.argmax(self.arr, axis=1)
        max_2 = []
        for i, m in enumerate(max):
            try:
                off = (np.argmax(self.arr[i, m-1:m+2:1]))
                if off == 1: 
                    max_2.append(m+1)
                else: max_2.append(m-1)
            except:
                max_2.append(1)
        center = []
        for m1, m2 in zip(max, max_2):
            center.append(0.5*(m1+m2))
        return center
    
    def calcAreas(self)->np.ndarray:
        delta = self.a+self.h
        colCenters = np.arange(self.h+0.5*self.a, self.cols*delta, delta)
        areas = np.zeros_like(colCenters)
        areas = np.pi*((colCenters+0.5*self.a)**2-(colCenters-0.5*self.a)**2)
        return(areas)
        
    def exData(self, areas, centers, glue=2, printIndividual=False):
        liq = self.df['m_l'].to_numpy()
        time = self.df['time [s]'].to_numpy()
        dens = self.df['rho_l'].to_numpy()
        rel = []
        zero = int(self.current_it-3)
        for i, c in enumerate(centers):
            if c > 57:
                left = self.arr[i, :int(c-0.5)][::-1]
                right = self.arr[i, int(c-0.5):]
            else: 
                left = self.arr[i, :int(c+0.5)][::-1]
                right = self.arr[i, int(c+0.5):]
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
            if printIndividual:
                print(f'Relative Difference: {"%.3f" % (diff/input*100)}%')
            self.exportDF['exDelta'].iloc[zero+i] = diff/input*100
            if diff/input*100 < 100:
                rel.append(diff/input*100)
        print('----')
        print(f'Average: {"%.3f" % np.mean(np.array(rel))}%')
    
    def fit_lorentz(self, centers, r_limit=0.95):
        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        params = []
        integ = []
        r_2 = []
        delta = self.a+self.h
        x_data = np.arange(self.h+0.5*self.a, self.cols*delta, delta)
        time = self.df['time [s]'].to_numpy()
        w = 0
        non_zero_rows = np.any(self.arr != 0, axis=1)

        for i in range(len(self.arr)):
            if non_zero_rows[i] == False: 
                r_2.append(np.nan)
                params.append([np.nan, np.nan, np.nan])
                integ.append(np.nan)
                continue
            c = centers[i]
            left = self.arr[i, :int(c-0.5)][::-1]/time[i]
            right = self.arr[i, int(c-0.5):]/time[i]
            
            w_n = np.argmax(left[left>0][::-1]) + np.argmax(right[right>0][::-1])
            if w < w_n: w = w_n

            max = np.max(self.arr[i, :])
            max_point = np.argmax(self.arr[i, :])
            FWHM = abs(find_nearest(left, max/2) - find_nearest(right, max/2))


            popt, pcov, id, mesg, ier  = curve_fit(self.lorentz, xdata=x_data, ydata=self.arr[i, :]/time[i], method='lm', p0=[max, x_data[max_point], FWHM], xtol=1e-9, gtol=1e-9, full_output=True)
            # print(id['nfev'])
            
            try:
                y, err = quad(self.lorentz, -np.inf, np.inf, args=(popt[0],popt[1],popt[2], ))    
                integ.append(y)
                y_fit = self.lorentz(x_data, *popt)
                y_data = np.concatenate((left[::-1], right))
                r_squared = r2_score(y_data, y_fit)
                if r_squared > r_limit:
                    r_2.append(r_squared)
                    params.append([abs(x) for x in popt])
                else: raise ValueError
            except:
                r_2.append(np.nan)
                params.append([np.nan, np.nan, np.nan])

        return [params, integ, r_2, w]
    
    def lorentzVolume(self, params, width, glue=2): 
        a, c, w = params
        delta = self.a+self.h
        liq = self.df['m_l'].to_numpy()[0]
        time = np.mean(self.df['time [s]'].to_numpy())
        dens = self.df['rho_l'].to_numpy()[0]
        x_data = np.linspace(0, 0.5*width*delta, 1000)
        gap = x_data[1]
        h = self.lorentz(x_data, a, 0, w)*time-glue

        area = np.pi*((x_data+gap)**2-(x_data)**2)
        volume = np.sum(h*area)
        
        if dens == 1236.27:
                volume = volume*(1-0.0431)
        if dens == 1222.96:
            volume = volume*(1-0.0163)

        input = liq/3600*time # input in kg
        diff = input-volume*dens*1e-9
        print('Fitted:')
        print(f'Relative Difference: {"%.3f" % (diff/input*100)}%')
        
        zero = int(self.current_it-3)
        for i in range(3):
            self.exportDF['fitDelta'].iloc[zero+i] = diff/input*100
        pass
    
    def exDataPDA(self, areas, centers, glue=2, printIndividual=False):
        liq = self.df['m_l'].to_numpy()
        time = self.df['time [s]'].to_numpy()
        dens = self.df['rho_l'].to_numpy()
        rel = []
        zero = int(self.current_it-3)
        delta = self.a+self.h
        for i, c in enumerate(centers):
            if c > 57:
                left = self.arr[i, :int(c-0.5)][::-1]
                right = self.arr[i, int(c-0.5):]
            else: 
                left = self.arr[i, :int(c+0.5)][::-1]
                right = self.arr[i, int(c+0.5):]
            factor = areas/(self.a*self.b)/2
            PDA_width = self.df['PDA'][zero+i]
            left = left[:int(np.ceil(0.5*PDA_width/delta))]
            right = right[:int(np.ceil(0.5*PDA_width/delta))]

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
            if printIndividual:
                print(f'Relative Difference: {"%.3f" % (diff/input*100)}%')
            self.exportDF['exPDA'].iloc[zero+i] = total/input*100
            if diff/input*100 < 100:
                rel.append(diff/input*100)

    def lorentzVolumePDA(self, params, glue=2):
        a, c, w = params
        delta = self.a+self.h
        liq = self.df['m_l'].to_numpy()[0]
        time = np.mean(self.df['time [s]'].to_numpy())
        dens = self.df['rho_l'].to_numpy()[0]
        width  = self.df['PDA'][self.current_it-3]
        x_data = np.linspace(0, 0.5*width, 1000)
        gap = x_data[1]
        h = self.lorentz(x_data, a, 0, w)*time-glue

        area = np.pi*((x_data+gap)**2-(x_data)**2)
        volume = np.sum(h*area)
        
        if dens == 1236.27:
                volume = volume*(1-0.0431)
        if dens == 1222.96:
            volume = volume*(1-0.0163)

        input = liq/3600*time # input in kg
        diff = input-volume*dens*1e-9
        print('Fitted:')
        print(f'Relative Difference: {"%.3f" % (diff/input*100)}%')
        
        zero = int(self.current_it-3)
        for i in range(3):
            self.exportDF['fitPDA'].iloc[zero+i] = volume*dens*1e-9/input*100
        pass

    @staticmethod
    def lorentz(x, A, xc, w):
            return A*(w/(4*(x-xc)**2+w**2))
        
    def run(self)->pd.DataFrame:
        for i in range(int(self.it)):
            # try:
                centers = self.findCenter()
                areas = self.calcAreas()
                self.exData(areas, centers, printIndividual=True)

                params, integ, r_2, width = self.fit_lorentz(centers)
                a_mean = 0
                w_mean = 0
                xc_mean = 0
                for p, r in zip(params, r_2):
                    if r == np.nan or np.nan in p: continue
                    a, xc, w = p
                    a_mean += r**3*a
                    w_mean += r**3*w
                    xc_mean += r**3*xc
                r_2 = np.array(r_2)
                a_mean /= np.nansum(r_2**3)
                w_mean /= np.nansum(r_2**3)
                xc_mean /= np.nansum(r_2**3)

                
                p_inf = [a_mean, xc_mean, w_mean]
                print('----')
                print(f'Mean R**2: {"%.3f"%np.nanmean(r_2)}')
                self.lorentzVolume(p_inf, width)
                print(f'Width: {"%.3f" % (width*(self.a+self.h))} mm')
                print(f'Parameters: {["%.3f"% x for x in p_inf]}')
                print('----')

                zero = int(self.current_it-3)
                for i in range(3):
                    self.exportDF['Width[mm]'].iloc[zero+i] = width*(self.a+self.h)
                    self.exportDF['Fit-R2'].iloc[zero+i] = r_2[i]
                self.exDataPDA(areas, centers)
                self.lorentzVolumePDA(p_inf)
            # except: pass
        
        self.exportDF = self.exportDF.fillna('n/a')
        return self.exportDF

if __name__ == '__main__':
    pat = pat(r'C:\Users\david\Documents\Dev\Atomizer-Toolbox\test\patternator.xlsx')
    df = pat.run()
    df.to_excel(r'C:\Users\david\Documents\Dev\Atomizer-Toolbox\test\patternator_ex.xlsx')
