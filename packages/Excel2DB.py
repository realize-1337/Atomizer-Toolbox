import os
import sqlite3
import pandas as pd
import re
import shutil

class Excel2DB():
    def __init__(self, db:str, fullEx = None) -> None:
        self.db = sqlite3.connect(db)
        self.fullEx = fullEx

    def convert(self, file, sheet_name, table_name):
        df = pd.read_excel(file, sheet_name=sheet_name)

        header = df.columns
        header = list(header[1:])
        header.insert(0, 'x')
        df.columns = header
        sortedHeader = ['x', '1H', '2H', 'VP', 'mean', 'std', 'pos', 'neg']
        df = df[sortedHeader]

        if sheet_name == 'D32 Export':
            df.iloc[0] = ['mm', 'µm', 'µm', 'µm', 'µm', 'µm', 'µm', 'µm',]
            df.iloc[1] = ['x', '1H', '2H', 'VP', 'mean', 'std', 'pos', 'neg']
            df.iloc[2] = ['Horizontal Position', 'Droplet Diameter', 'Droplet Diameter', 'Droplet Diameter', 'Droplet Diameter', 'Droplet Diameter', 'Droplet Diameter', 'Droplet Diameter']
        if sheet_name == 'v_z Export':
            df.iloc[0] = ['mm', 'm/s', 'm/s', 'm/s', 'm/s', 'm/s', 'm/s', 'm/s',]
            df.loc[1] = ['x', '1H', '2H', 'VP', 'mean', 'std', 'pos', 'neg']
            df.iloc[2] = ['Horizontal Position', 'Droplet Axial Velocity', 'Droplet Axial Velocity', 'Droplet Axial Velocity', 'Droplet Axial Velocity', 'Droplet Axial Velocity', 'Droplet Axial Velocity', 'Droplet Axial Velocity']

        df = df.set_index('x', drop=True)
        df.to_sql(table_name, self.db, if_exists='replace')

        if self.fullEx:
            with pd.ExcelWriter(self.fullEx, 'openpyxl', if_sheet_exists='replace', mode='a') as ex:
                df.to_excel(ex, sheet_name=f'{sheet_name} {table_name}')


if __name__ == '__main__':
    topFolder = 'F:\\'
    pattern = r'.*(Duese.*)\\'
    found = []
    for root, sub, files in os.walk(topFolder):
        for file in files:
            if file.startswith('PDA') and file.endswith('.xlsx'):
                found.append(os.path.join(root, file))

    print(found)
    names = []
    for file in found:
        l = re.findall(pattern, file)[0].split('\\')
        names.append(f'{l[0]} {l[1]} {l[2]}')

    db = r'C:\Users\david\Desktop\Test PDA\test.db'
    fullEx = r'C:\Users\david\Desktop\Test PDA\full.xlsx'
    ex2db = Excel2DB(db, fullEx)

    folder = r'C:\Users\david\Desktop\Test PDA\All'
    if not os.path.exists(folder):
        os.mkdir(folder)

    for file, name in zip(found, names):
        try:
            ex2db.convert(file, 'D32 Export', name)
            ex2db.convert(file, 'v_z Export', name)
            shutil.copy(file, os.path.join(folder, f'{name}.xlsx'))
        except: 
            pass
