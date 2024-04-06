import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
            centers = np.concatenate((np.arange(0, 21, 2), np.arange(25, abs(np.min(x_data))+5, 5)))
            steps = np.concatenate((np.zeros(1), np.diff(centers)))
            Raw_Area = np.pi * ((centers+0.5*steps)**2 - (centers-0.5*steps)**2)
            Raw_Area[0] = np.pi * (0.5*steps[1])**2
            if np.max(x_data) > 0:
                Area =  np.concatenate((Raw_Area[::-1], Raw_Area[1:]))/2
                Area[int(len(Area)/2)] *= 2
                y_data = m_flux*Area*60
                flux_y_data = m_flux
                ratio_flux = r
            else:
                x_data = np.concatenate((x_data, x_data[::-1][1:]*-1))
                Area = Raw_Area[::-1]/2
                Area[-1] *= 2
                y_data = np.concatenate((m_flux*Area, (m_flux*Area)[::-1][1:]))*60
                flux_y_data = np.concatenate((m_flux, (m_flux)[::-1][1:]))
                ratio_flux = np.concatenate((r, (r)[::-1][1:]))
            data.append(go.Scatter(x=x_data, y=y_data, name=f'{names[i]}', line_shape='hvh', mode='lines'))
            flux_data.append(go.Scatter(x=x_data, y=flux_y_data, name=f'{names[i]}', line_shape='hvh', mode='lines'))
            ratio.append(go.Scatter(x=x_data, y=ratio_flux, name=f'{names[i]}', line_shape='hvh', mode='lines'))
        

        fig = go.Figure(data)
        fig.update_layout(title=f'Mass distribution {exportName}')
        fig.write_html(os.path.join(exportPath, 'mass', exportName))
        
        fig = go.Figure(flux_data)
        fig.update_layout(title=f'Mass flux density {exportName}')
        fig.write_html(os.path.join(exportPath, 'flux', exportName))
        
        fig = go.Figure(ratio)
        fig.update_layout(title=f'm_flux / n_flux ratio  {exportName}')
        fig.write_html(os.path.join(exportPath, 'ratio', exportName))

        fig = self.createMap(x_data, y_data, name=exportName)
        fig.write_html(os.path.join(exportPath, 'maps', exportName))
        
        fig = self.createMap(x_data, flux_y_data, name=exportName, z_name='Qulitative normalized mass flux density')
        fig.write_html(os.path.join(exportPath, 'maps_flux', exportName))


    def createMap(self, x_data:np.ndarray, z_data:np.ndarray, resolution:int = 100, name='Normalized mass distribution', z_name='Qualitative mass'):
        
        x = np.copy(x_data[x_data<=0])
        z = z_data[:len(x)]
        ang = np.linspace(0, 0.5*np.pi, resolution)
        fineX = np.linspace(np.min(x), np.max(x), resolution)
        fineZ = np.interp(fineX, x, z)
        posCord = np.zeros((len(fineX),len(fineX), 3))
        
        for i in range(len(fineX)):
            for j in range(len(ang)):
                posCord[i,j,0] = abs(np.cos(ang[j]))*fineX[i]
                posCord[i,j,1] = abs(np.sin(ang[j])*fineX[i])
                posCord[i,j,2] = fineZ[i]
         
         
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
        
        
        arr2d[:, 2] /= np.max(arr2d[:,2])
        fig = go.Figure(go.Mesh3d(x=arr2d[:, 0].flatten(), y=arr2d[:, 1].flatten(), z=arr2d[:, 2].flatten(),
                                   colorscale='rainbow',
                                   intensity=arr2d[:, 2].flatten(), 
                                   opacity=0.5))
        
        fig.update_layout(scene=dict(xaxis=dict(range=[-100, 100]),
                              yaxis=dict(range=[-100, 100]),
                              zaxis_title=z_name, 
                              xaxis_title='x Position in mm', 
                              yaxis_title='y Position in mm'), 
                              title=name)
        
        return fig



    def run(self):
        for report in tqdm(self.reports):
            dfs = self.readReport(report)
            name = f'{os.path.dirname(report)}'[2:].replace('\\', '-')
            try:
                self.createGraphs(dfs, r'C:\Users\david\Documents\Dev\Atomizer-Toolbox\test\PDA_extractor\export', f'{name}.html')
            except: print(f'WARNING: {name}')




if __name__ == '__main__':
    extractor = PDA_extractor(r'H:')
    extractor.run()

