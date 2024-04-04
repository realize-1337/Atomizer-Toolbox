import numpy as np
import pandas as pd
import plotly.graph_objects as go
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
        fig.write_html(os.path.join(exportPath, 'mass', exportName))
        
        fig = go.Figure(flux_data)
        fig.write_html(os.path.join(exportPath, 'flux', exportName))
        
        fig = go.Figure(ratio)
        fig.write_html(os.path.join(exportPath, 'ratio', exportName))

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

