import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import curve_fit
from scipy.integrate import quad
from sklearn.metrics import r2_score
import os
from tqdm import tqdm


class PDA_extractor():
    def __init__(self, path, a=5.5, b=5.5, h=0.35 ) -> None:
        self.path = path
        self.reports = []
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith('xlsx') and file.startswith('PDA'):
                    self.reports.append(os.path.join(root, file))

   
    def readReport(self, report:str|os.PathLike):
        df_1H = pd.read_excel(report, sheet_name='1H', header=3, skipfooter=4)
        df_2H = pd.read_excel(report, sheet_name='2H', header=3, skipfooter=4)
        df_VP = pd.read_excel(report, sheet_name='VP', header=3, skipfooter=4)
        
        return [df_1H, df_2H, df_VP]

    def createGraphs(self, dfs:list, exportPath, exportName):
        data = []
        flux_data = []
        ratio = []
        names = {
            0: '1H', 
            1: '2H', 
            2: 'VP'
        }
        for i, df in enumerate(dfs):
            df:pd.DataFrame
            x_data = df['x [mm]'].to_numpy()
            m_flux = df['m_flux [kg/(s mm^2)]'].to_numpy()
            n_flux = df['n_flux [1/(s mm^2)]'].to_numpy()
            r = m_flux/n_flux
            centers = np.concatenate((np.arange(0, 21, 2), np.arange(25, abs(np.min(x_data))+5, 5))).astype(np.float32)
            diffI = np.concatenate((np.zeros(1), np.diff(centers)))/2
            diffO = np.concatenate((np.diff(centers), np.zeros(1)))/2
            diffO[-1] = 2.5
            border = np.vstack((diffI, diffO))
            border = np.vstack((border, centers))
   
            Raw_Area = np.zeros_like(centers)
            Raw_Area = np.pi * ((centers+diffO)**2 - (centers-diffI)**2)
            
            if np.max(x_data) > 0:
                Area =  np.concatenate((Raw_Area[::-1], Raw_Area[1:]))/2
                Area[int(len(Area)/2)] *= 2
                y_data = m_flux*Area*3600
                flux_y_data = m_flux
                ratio_flux = r
            else:
                x_data = np.concatenate((x_data, x_data[::-1][1:]*-1))
                Area = Raw_Area[::-1]/2
                Area[-1] *= 2
                y_data = np.concatenate((m_flux*Area, (m_flux*Area)[::-1][1:]))*3600
                flux_y_data = np.concatenate((m_flux, (m_flux)[::-1][1:]))
                ratio_flux = np.concatenate((r, (r)[::-1][1:]))

            # fineX = np.linspace(np.min(x_data), np.max(x_data), 1000)
            # fineZ = np.interp(fineX, x_data, flux_y_data)
            # fig = go.Figure(go.Scatter(x=fineX, y=fineZ))
            # fig.show()

            data.append(go.Scatter(x=x_data, y=y_data, name=f'{names[i]}', line_shape='hvh', mode='lines'))
            flux_data.append(go.Scatter(x=x_data, y=flux_y_data, name=f'{names[i]}', line_shape='hvh', mode='lines'))
            ratio.append(go.Scatter(x=x_data, y=ratio_flux, name=f'{names[i]}', line_shape='hvh', mode='lines'))
            # print(np.sum(y_data[:-1]))
        

        fig = go.Figure(data)
        fig.update_layout(title=f'Mass distribution {exportName}')
        fig.write_html(os.path.join(exportPath, 'mass', exportName))
        
        fig = go.Figure(flux_data)
        fig.update_layout(title=f'Mass flux density {exportName}')
        fig.write_html(os.path.join(exportPath, 'flux', exportName))
        
        fig = go.Figure(ratio)
        fig.update_layout(title=f'm_flux / n_flux ratio  {exportName}')
        fig.write_html(os.path.join(exportPath, 'ratio', exportName))
        
        fig, mass = self.createMap(x_data, flux_y_data, name=exportName, z_name='Mass fraction in each annulus in %')
        fig.write_html(os.path.join(exportPath, 'maps', exportName))
        
        fig, mass = self.createMap(x_data, flux_y_data, name=exportName, z_name='Cumulative mass fraction within the diameter', mode='cumulative')
        fig.write_html(os.path.join(exportPath, 'maps_cumulative', exportName))

        return mass

    def createMap(self, x_pos:np.ndarray, flux:np.ndarray, percentageWidth:float = 0.5, name='Normalized mass distribution', z_name='Qualitative mass', mode='regular', drawCricles=False):
        
        resolution_x = int(1/percentageWidth*100)
        x_data, z_data = self.fit_lorentz(x_pos, flux, resolution_x)

        fineZ = z_data[x_data<=0]
        mass = np.sum(fineZ)  
        if mode == 'cumulative':
            fineZ = np.cumsum(fineZ[::-1])[::-1]
            mass = np.max(fineZ)
        fineX = x_data[x_data<=0]
        if drawCricles:
            circles = []
        ang = np.linspace(0, 0.5*np.pi, len(fineX))
        posCord = np.zeros((len(fineX),len(ang), 3))     
        
        for i in range(len(fineX)):
            circ = np.zeros((len(ang),3))
            for j in range(len(ang)):
                posCord[i,j,0] = abs(np.cos(ang[j]))*fineX[i]
                posCord[i,j,1] = abs(np.sin(ang[j])*fineX[i])
                posCord[i,j,2] = fineZ[i]
                circ[j,0] = abs(np.cos(ang[j]))*fineX[i]
                circ[j,1] = abs(np.sin(ang[j])*fineX[i])
                circ[j,2] = fineZ[i]
            if drawCricles: circles.append(circ)

        
        total = len(fineX)**2
        arr2d = posCord.reshape((total, 3))
        arr2d_neg_pos = np.copy(arr2d)
        arr2d_neg_neg = np.copy(arr2d_neg_pos)
        arr2d_neg_neg[:,1] = arr2d_neg_neg[:,1]*-1
        arr2d_pos_neg = np.copy(arr2d_neg_neg)
        arr2d_pos_neg[:,0] *= -1
        arr2d_pos_pos = np.copy(arr2d_neg_pos)
        arr2d_pos_pos[:,0] *= -1
        arr2d = np.concatenate((arr2d_pos_pos, arr2d_neg_neg, arr2d_pos_neg, arr2d_neg_pos), axis=0)
        
        
        # arr2d[:, 2] /= np.max(arr2d[:,2])
        arr2d[:, 2] /= mass
        arr2d[:, 2] *= 100
        # print(vol)
        # df = pd.DataFrame(arr2d)
        # df.to_excel(r'C:\Users\david\Documents\Dev\Atomizer-Toolbox\test\PDA_extractor\test.xlsx')
        if mode != 'cumulative':
            fig = go.Figure(go.Mesh3d(x=arr2d[:, 0].flatten(), y=arr2d[:, 1].flatten(), z=arr2d[:, 2].flatten(),
                                    colorscale='rainbow',
                                    intensity=arr2d[:, 2].flatten(), 
                                    opacity=0.5))
                        
            fig.update_layout(scene=dict(xaxis=dict(range=[-100, 100]),
                                yaxis=dict(range=[-100, 100]),
                                zaxis_title=f'{z_name} with annulus of {"%.1f" %(1/resolution_x*100/2)} % of full width', 
                                xaxis_title='x Position in mm', 
                                yaxis_title='y Position in mm'), 
                                title=f'{name} Spray width: {"%.2f" %(abs(np.min(x_pos))*2)} mm. Annulus width = {"%.2f" %(abs(np.min(x_pos))/resolution_x)} mm')

            if drawCricles:
                for circ in circles:
                    fig.add_trace(go.Scatter3d(
                        x=circ[:,0],
                        y=circ[:,1],
                        z=circ[:,2]/mass*100,
                        mode='lines',
                        marker=dict(
                            color='black',  # You can adjust the color as needed
                            opacity=0.2,    # You can adjust the opacity as needed
                            line=dict(width=0)  # Remove marker border
                        ),
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter3d(
                        x=circ[:,0]*-1,
                        y=circ[:,1],
                        z=circ[:,2]/mass*100,
                        mode='lines',
                        marker=dict(
                            color='black',  # You can adjust the color as needed
                            opacity=0.2,    # You can adjust the opacity as needed
                            line=dict(width=0)  # Remove marker border
                        ),
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter3d(
                        x=circ[:,0],
                        y=circ[:,1]*-1,
                        z=circ[:,2]/mass*100,
                        mode='lines',
                        marker=dict(
                            color='black',  # You can adjust the color as needed
                            opacity=0.2,    # You can adjust the opacity as needed
                            line=dict(width=0)  # Remove marker border
                        ),
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter3d(
                        x=circ[:,0]*-1,
                        y=circ[:,1]*-1,
                        z=circ[:,2]/mass*100,
                        mode='lines',
                        marker=dict(
                            color='black',  # You can adjust the color as needed
                            opacity=0.2,    # You can adjust the opacity as needed
                            line=dict(width=0)  # Remove marker border
                        ),
                        showlegend=False
                    ))
        else:
            fig = go.Figure(go.Mesh3d(x=arr2d[:, 0].flatten(), y=arr2d[:, 1].flatten(), z=arr2d[:, 2].flatten(),
                                    colorscale='rainbow',
                                    intensity=arr2d[:, 2].flatten(), 
                                    opacity=0.5))
            
            fig.update_layout(scene=dict(xaxis=dict(range=[-100, 100]),
                                yaxis=dict(range=[-100, 100]),
                                zaxis_title=f'{z_name}', 
                                xaxis_title='x Position in mm', 
                                yaxis_title='y Position in mm'), 
                                title=f'{name} Cumulative mass fraction within the diameter')
        return [fig, mass]

    def fit_lorentz(self, x_pos:np.ndarray, flux:np.ndarray, res=100):
        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        max_point = int(len(x_pos)/2)
        max = flux[max_point]
        FWHM = abs(find_nearest(x_pos[x_pos<x_pos[max_point]], max/2) - find_nearest(x_pos[x_pos>x_pos[max_point]], max/2))


        popt, pcov, id, mesg, ier  = curve_fit(self.lorentz, xdata=x_pos, ydata=flux, method='lm', p0=[max, x_pos[max_point], FWHM], xtol=1e-9, gtol=1e-9, full_output=True)
        

        borders = np.linspace(0, abs(np.min(x_pos)), res)
        centers = np.linspace(0, abs(np.min(x_pos)), res)
        # diff = np.diff(borders)
        # borders = borders[1:]
        # centers = borders-diff/2
        diffI = np.diff(centers, prepend=0)
        last = abs(np.min(x_pos)) + abs(np.min(x_pos))/(res-1)*0.5
        diffO = np.diff(centers, append=last)
        y_fit = self.lorentz(centers, *popt)
        y_fit = np.concatenate((y_fit[::-1], y_fit[1:]))
        # fig = go.Figure(go.Scatter(x=centers, y=y_fit))
        # fig.show()

        Raw_Area = np.zeros_like(centers)
        Raw_Area = np.pi * ((centers+diffO)**2 - (centers-diffI)**2)

        Area =  np.concatenate((Raw_Area[::-1], Raw_Area[1:]))/2
        Area[int(len(Area)/2)] *= 2
        y_data = y_fit*Area*3600
    
        centers = np.concatenate((centers[::-1]*-1, centers[1:]))
        return [centers, y_data]
    
    @staticmethod
    def lorentz(x, A, xc, w):
            return A*(w/(4*(x-xc)**2+w**2))

    def run(self, debug=False):
        av = []
        for report in (self.reports):
            dfs = self.readReport(report)
            name = f'{os.path.dirname(report)}'[2:].replace('\\', '-')
            if debug:
                print('\n' + name)
                self.createGraphs(dfs, r'C:\Users\david\Documents\Dev\Atomizer-Toolbox\test\PDA_extractor\export', f'{name}.html')
            else:
                try:
                    print('\n' + name)
                    liq = float(name.split('-')[2].split('_')[1].replace(',', '.'))
                    mass = self.createGraphs(dfs, r'C:\Users\david\Documents\Dev\Atomizer-Toolbox\test\PDA_extractor\export', f'{name}.html')
                    av.append((liq-mass)/liq)
                except: print(f'WARNING: {name}')
        
        arr = np.array(av)
        print(f'Average: {np.mean(arr)}')




if __name__ == '__main__':
    extractor = PDA_extractor(r'H:')
    extractor.run()

