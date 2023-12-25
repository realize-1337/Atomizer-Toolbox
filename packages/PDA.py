import os
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from openpyxl import load_workbook

def createPowerFit(x, y):
    def func(x, a, b):
        return a * np.power(x, b)

    popt, _ = curve_fit(func, x, y)
    return popt

def createLogFit(x, y):
    def func(x, a, b):
        return a * np.log(x) + b

    popt, _ = curve_fit(func, x, y)
    return popt

class PDA():
    def __init__(self, path, upperCutOff = 1040.34, lowerCutOff = 0, posLine = 3, firstDataLine = 6, velCol = 3, diaCol = 6, timeCol = 1, split = '\t', phi = 70, f_1 = 1000, f_2 = 310, ls_p = 200, liqDens = 998.2, header=['Row', 'AT', 'TT', 'Vel', 'U12', 'U13', 'Diameter']) -> None:
        self.path = path
        self.posLine = posLine
        self.firstDataLine = firstDataLine
        self.velCol = velCol
        self.diaCol = diaCol
        self.timeCol = timeCol
        self.splitter = split
        self.header = header
        self.upperCutOff = upperCutOff
        self.lowerCutOff = lowerCutOff
        self.phi = np.deg2rad(phi)
        self.f_1 = f_1
        self.f_2 = f_2
        self.ls_p = ls_p
        self.liqDens = liqDens

    def findPos(self, file):
        lines = ''
        with open(file, 'r') as f:
            lines = f.readlines()
            f.close()
        pos = lines[self.posLine].split(';')
        x = float(pos[1].split(' ')[0])
        y = float(pos[2].split(' ')[0])
        z = float(pos[3].split(' ')[0])
        return [x, y, z]
        
    def pandasFromCSV(self, file) -> pd.DataFrame:
        df = pd.read_csv(file, sep=self.splitter, skiprows=self.firstDataLine, names=self.header)
        # print(df)
        df = df[df['Diameter'] <= self.upperCutOff]
        df = df[df['Diameter'] > 0]
        df = df[df['Vel'] != 0]
        return df
    
    def calcDias(self, df:pd.DataFrame()) -> list:
        D10 = df['Diameter'].mean()
        D20 = ((df['Diameter']**2).mean())**0.5
        D30 = ((df['Diameter']**3).mean())**(1/3)
        D32 = sum(df['Diameter']**3)/sum(df['Diameter']**2)

        dias_raw:pd.Series = df['Diameter'].sort_values()
        vols = (dias_raw**3).cumsum()
        max = vols.iloc[-1]
        
        DV10 = dias_raw[vols <= 0.1 * max].max()
        DV50 = dias_raw[vols <= 0.5 * max].max()
        DV90 = dias_raw[vols <= 0.9 * max].max()

        return [D10, D20, D30, D32, DV10, DV50, DV90]

    def calcArea(self, df:pd.DataFrame):
        D = df['Diameter'].to_numpy()
        Ttime = df['TT'].to_numpy()
        LDA1 = df['Vel'].to_numpy()
        LDA4 = np.zeros(len(LDA1))
        burst_length = Ttime * np.sqrt(np.square(LDA1) + np.square(LDA4))
        Data_new = np.column_stack((D, Ttime, LDA1, LDA4, burst_length))
        Data_new = pd.DataFrame(Data_new, columns=['D', 'Ttime', 'LDA1', 'LDA4', 'burst_length'])
        Data_new_sort = Data_new.sort_values(by=['D'])

        bingroesse = 5
        bincount = 200

        edges = np.arange(0, np.ceil(np.max(D)) + bingroesse, bingroesse)
        N, edges = np.histogram(Data_new_sort['D'], bins=edges)
        # print(N)
        # print(len(N))
        Data_bin = [None]*len(N)

        count = N[0]
        # if count == 0: count = 1
        Data_bin[0] = Data_new_sort.iloc[: count, :]
        # print(Data_bin)
        
        for i in range(1, len(N)):
            # print(count)
            Data_bin[i] = Data_new_sort.iloc[count: count+N[i], :]
            count = count + N[i]

        mean_burstlen = np.zeros(len(N))
        mean_burstlensquared = np.zeros(len(N))

        for i in range(len(N)):
            mean_burstlen[i] = (Data_bin[i]['burst_length']).mean()
            mean_burstlensquared[i] = mean_burstlen[i]**2
        

        edges_middle = edges[0:-1] + bingroesse/2
        # print(mean_burstlensquared)

        # print(np.isnan(mean_burstlensquared))
        fit_x = edges_middle[np.isfinite(mean_burstlensquared)]
        fit_y = mean_burstlensquared[np.isfinite(mean_burstlensquared)]
        anz_pro_bin = np.transpose(N)
        anz_pro_bin = anz_pro_bin[np.isfinite(mean_burstlensquared)]
    
        sort_anz_pro_bin = np.sort(anz_pro_bin)
        if sort_anz_pro_bin[-1] < bincount:
            bincount = np.mean(anz_pro_bin)

        fit_x = fit_x[anz_pro_bin >= bincount]
        fit_y = fit_y[anz_pro_bin >= bincount]

        powA, powB = createPowerFit(fit_x, fit_y)
        logA, logB = createLogFit(fit_x, fit_y)
        x = np.arange(0, np.max(np.ceil(D))+1)
        y_power = powA*x**powB
        y_log = logA*np.log(x)+logB

        y_diff = abs(y_power-y_log)
        I = np.argsort(y_diff)
        sorted_x = np.sort(x[I[:5]])
        x_pow_max = np.max(sorted_x)

        beta = -self.f_2/self.f_1
        ls_korr = self.ls_p/abs(beta)
        D_val = np.zeros(len(D))
        A_val = np.zeros(len(D))

        for i in range(len(D)):
            if D[i] < x_pow_max:
                numerator = (4 / np.pi) * ((ls_korr * (np.sqrt(powA * D[i] ** powB))) /
                                        (ls_korr - np.cos(self.phi) * np.sqrt(powA * D[i] ** powB) *
                                            np.abs(LDA4[i] / np.sqrt(LDA1[i] ** 2 + LDA4[i] ** 2))))
                D_val[i] = numerator
            else:
                numerator = (4 / np.pi) * ((ls_korr * (np.sqrt(logA * np.log(D[i]) + logB))) /
                                        (ls_korr - np.cos(self.phi) * np.sqrt(logA * np.log(D[i]) + logB) *
                                            np.abs(LDA4[i] / np.sqrt(LDA1[i] ** 2 + LDA4[i] ** 2))))
                D_val[i] = numerator

        for i in range(len(D)):
            A_val[i] = (D_val[i] * ls_korr / np.sin(self.phi)) - (np.pi * (D_val[i] ** 2) / 4 / np.tan(self.phi)) * (
                    np.abs(LDA4[i]) / np.sqrt(LDA1[i] ** 2 + LDA4[i] ** 2))

        return D_val, A_val

    def calcFlux(self, A_Val:np.array, t_ges:float, dia_arr:pd.Series):
        print(np.count_nonzero(np.isnan(A_Val)))
        n_flux = 1/t_ges * np.sum(1./A_Val)*10**6
        m_flux = 1/t_ges * np.sum(10**(-18)*self.liqDens*(np.pi/6.*dia_arr**3./A_Val))*10**6

        return [n_flux, m_flux]

    def calcID32(self, fullDict:dict, dir:str) -> list:
        max = -np.inf
        min = np.inf

        for k, v in fullDict.items():
            if float(k) > max: max = float(k)
            if float(k) < min: min = float(k)
        
        df = pd.DataFrame(fullDict).transpose().reset_index(drop=True)

        if abs(max)-abs(min) == 0:
            mode = 'VP'
            df = df.sort_values(by=dir, ascending=True).reset_index(drop=True)
            # r_i = np.zeros(int(np.ceil(len(df)/2)))
            r_i = np.zeros(len(df))
            delta_r = np.zeros(int(np.ceil(len(r_i)/2)))
        elif abs(max)-abs(min) > 0:
            mode = 'HP_pos'
            df = df.sort_values(by=dir, ascending=True).reset_index(drop=True)
            r_i = np.zeros(len(df.where(df[dir]>=0)))
            delta_r = np.zeros(len(r_i))
        else:
            mode = 'HP_neg'
            df = df.sort_values(by=dir, ascending=True).reset_index(drop=True)
            r_i = np.zeros(len(df.where(df[dir]<=0)))
            delta_r = np.zeros(len(r_i))
        
        d_32_i = np.zeros(len(r_i))
        d_20_i = np.zeros(len(r_i))
        d_30_i = np.zeros(len(r_i))
        n_flux_i = np.zeros(len(r_i))
        m_flux_i = np.zeros(len(r_i))

        for i in range(len(r_i)):
            r_i[i] = df[dir].iloc[i]
            d_30_i[i] = df['D30'].iloc[i]
            d_20_i[i] = df['D20'].iloc[i]
            d_32_i[i] = df['D32'].iloc[i]
            n_flux_i[i] = df['n_flux'].iloc[i]
            m_flux_i[i] = df['m_flux'].iloc[i]
        
        if not mode == 'VP':
            r_i = np.concatenate([r_i, np.flip(r_i[:len(r_i)-1])*-1])
            d_30_i = np.concatenate([d_30_i, np.flip(d_30_i[:len(d_30_i)-1])])
            d_20_i = np.concatenate([d_20_i, np.flip(d_20_i[:len(d_20_i)-1])])
            d_32_i = np.concatenate([d_32_i, np.flip(d_32_i[:len(d_32_i)-1])])
            n_flux_i = np.concatenate([n_flux_i, np.flip(n_flux_i[:len(n_flux_i)-1])])
            m_flux_i = np.concatenate([m_flux_i, np.flip(m_flux_i[:len(m_flux_i)-1])])
        else:
            r_i = np.concatenate([r_i, np.flip(r_i[:len(r_i)-1])*-1])
            d_30_i = np.concatenate([d_30_i[:int(np.ceil(len(df)/2))], np.flip(d_30_i[:int(np.ceil(len(df)/2))-1])])
            d_20_i = np.concatenate([d_20_i[:int(np.ceil(len(df)/2))], np.flip(d_20_i[:int(np.ceil(len(df)/2))-1])])
            d_32_i = np.concatenate([d_32_i[:int(np.ceil(len(df)/2))], np.flip(d_32_i[:int(np.ceil(len(df)/2))-1])])
            n_flux_i = np.concatenate([n_flux_i[:int(np.ceil(len(df)/2))], np.flip(n_flux_i[:int(np.ceil(len(df)/2))-1])])
            m_flux_i = np.concatenate([m_flux_i[:int(np.ceil(len(df)/2))], np.flip(m_flux_i[:int(np.ceil(len(df)/2))-1])])

        # delta_r = np.zeros(int(np.ceil(len(r_i)/2)))
        for i in range(len(delta_r)):
            try: delta_r[i] = abs(df[dir].iloc[i]-df[dir].iloc[i+1])
            except: 
                if df[dir].iloc[i] == 0:
                    delta_r[i] = abs(df[dir].iloc[i-1])
                else: pass

        delta_r = np.concatenate([delta_r, np.flip(delta_r[1:])])
        areas = np.zeros(len(delta_r))

        for i in range(len(areas)):
            if r_i[i] == 0:
                areas[i] = np.pi * (delta_r[i]/2) ** 2 * 10**6
            else:
                areas[i] = np.pi * abs((r_i[i] - 0.5*delta_r[i])**2 - (r_i[i] + 0.5*delta_r[i])**2) * 10**6 / 2

        # print(df)

        ID_32_n = np.sum(d_30_i**3 * n_flux_i * areas)/np.sum(d_20_i**2 * n_flux_i * areas)
        ID_32_m = np.sum(d_30_i**3 * m_flux_i * areas)/np.sum(d_20_i**2 * m_flux_i * areas)
        
        units = ['[mm]', '[mm]', '[mm]', '[µm]', '[µm]', '[µm]', '[µm]', '[µm]', '[µm]', '[µm]', '[1/s]', '[m/s]', '[-]', '[µm]', '[1/(s mm^2)]', '[kg/(s mm^2)]']
        newCols = {col: f'{col} {item}' for col, item in zip(df.columns, units)}
        df = df.rename(columns=newCols).reset_index()

        # print(ID_32_n)
        # print(ID_32_m)
        
        # df_n = pd.DataFrame(d_30_i).transpose()
        # df_m = pd.DataFrame(d_20_i).transpose()

        # df_new = pd.concat([df_n, df_m]).transpose()
        # df_new.to_excel(os.path.join(self.path, 'testFlux.xlsx'))

        return [df, ID_32_n, ID_32_m]

    def writeToExcel(self, df, ID_32_n, ID_32_m, filename='export.xlsx'):
        maxId = len(df)+2

        export = os.path.join(self.path, filename)
        df.to_excel(export, index=False)

        workbook = load_workbook(export)
        sheet = workbook.active

        sheet[f'A{maxId}'] = 'ID_32_n [µm]'
        sheet[f'A{maxId+1}'] = 'ID_32_m [µm]'
        sheet[f'B{maxId}'] = ID_32_n
        sheet[f'B{maxId+1}'] = ID_32_m

        workbook.save(export)

    def run(self):
        fullDict_x = {}
        fullDict_y = {}
        for file in os.listdir(self.path):
            if file.endswith('.txt'):
                # self.readFile(os.path.join(self.path, file))
                x, y, z = self.findPos(os.path.join(self.path, file))
                innerDict = {}
                innerDict['x'] = x
                innerDict['y'] = y
                innerDict['z'] = z
                df = self.pandasFromCSV(os.path.join(self.path, file))
                if df.empty: continue
                t_ges = df['AT'].max()/1000 + df['TT'].iloc[-1]/(10**6) -df['AT'].min()/1000
                D10, D20, D30, D32, DV10, DV50, DV90 = self.calcDias(df)
                D_val, A_val = self.calcArea(df)
                n_flux, m_flux = self.calcFlux(A_val, t_ges, df['Diameter'])

                innerDict['D10'] = D10
                innerDict['D20'] = D20
                innerDict['D30'] = D30
                innerDict['D32'] = D32
                innerDict['DV10'] = DV10
                innerDict['DV50'] = DV50
                innerDict['DV90'] = DV90
                innerDict['Freq'] = len(df)/t_ges
                innerDict['v_z_mean'] = df['Vel'].mean()
                innerDict['n'] = len(df)
                innerDict['upperCut'] = self.upperCutOff
                innerDict['n_flux'] = n_flux
                innerDict['m_flux'] = m_flux
                
                if x == 0 and y != 0:
                    fullDict_x[f'{x}'] = innerDict
                elif x != 0 and y == 0:
                    fullDict_x[f'{x}'] = innerDict
                else:
                    fullDict_x[f'{x}'] = innerDict
                    fullDict_y[f'{y}'] = innerDict

        df_x, ID_32_n_x, ID_32_m_x = self.calcID32(fullDict_x, dir='x')

        self.writeToExcel(df_x, ID_32_n_x, ID_32_m_x)
        return(ID_32_n_x, ID_32_m_x)

if __name__ == '__main__':
    # _path = r'M:\Duese_4\Ole_Erw\2_60_34\VP'
    _path = r'M:\Duese_4\Ole_Erw\2_60_34\1H'

    pda = PDA(_path)
    pda.run()

