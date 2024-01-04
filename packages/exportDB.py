import os
import sqlite3
import pandas as pd
import numpy as np
import json

class exportDB():
    def __init__(self, path) -> None:
        self.db = sqlite3.connect(path)
        self.c = self.db.cursor()

    def writeData(self, df:pd.DataFrame, name):
        print(df)
        print(df.to_sql(name, self.db, if_exists='replace'))
        pass

    def writeExport(self, di:dict, name:str):
        create = f'CREATE TABLE IF NOT EXISTS \"{name}\" (row INT, col INT, ad1 TEXT, ad2 TEXT, ad3 TEXT);'
        self.c.execute(create)
        clear = f'DELETE FROM \"{name}\";'
        self.c.execute(clear)
        for row_id, v in di.items():
            if type(v) == str:
                match = False
                a1 = v
                a2 = None
                a3 = None
                if name == 'header': 
                    col_id = row_id
                    row_id = -1
                else: 
                    col_id = -1
                ins = f'INSERT INTO \"{name}\" (row, col, ad1, ad2, ad3) VALUES (?, ?, ?, ?, ?);'
                self.c.execute(ins, (int(row_id), int(col_id), a1, a2, a3))
                
            else:
                for col_id, l in v.items():
                    if l == None: 
                        a1 = None 
                        a2 = None 
                        a3 = None
                    else: 
                        if len(l) == 3: a1, a2, a3 = l
                        else: 
                            a1 = l
                            a2 = None
                            a3 = None
                    
                    ins = f'INSERT INTO \"{name}\" (row, col, ad1, ad2, ad3) VALUES (?, ?, ?, ?, ?);'
                    self.c.execute(ins, (int(row_id), int(col_id), a1, a2, a3))
            self.db.commit()

    def readExportOption(self) -> list:
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.c.fetchall()
        dictList = []
        for table in tables:
            table_name = table[0]
            print(table_name)
            self.c.execute(f"SELECT * FROM \"{table_name}\";")
            rows = self.c.fetchall()

            self.c.execute(f"PRAGMA table_info(\"{table_name}\");")
            columns = self.c.fetchall()
            dict = {}
            for i, col in enumerate(columns):
                if i == 0: continue
                innerDict = {}
                for row in rows:
                    innerDict[row[0]] = row[i]
                dict[col[1]] = innerDict
            dictList.append((dict, table_name))

        return dictList
    
    def DBtoDicts(self) -> list:
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.c.fetchall()
        dictList = []
        if len(tables) == 0: raise IndexError
        for i, table in enumerate(tables):
            print('-'*10)
            dict = {}
            table_name = table[0]
            self.c.execute(f"SELECT * FROM \"{table_name}\";")
            rows = self.c.fetchall()
            arr = pd.DataFrame(rows, columns=['row', 'col', 'ad1', 'ad2', 'ad3'])
            arr = arr.sort_values(by=['row', 'col'], ascending=True)
            if i == 0:
                grouped = arr.groupby(['row'])
                list_of_dfs = [group for _, group in grouped]
                for j, df in enumerate(list_of_dfs):
                    row = df['row'].iloc[0]
                    innerDict = {}
                    for k in range(len(df)):
                        s = df.iloc[k]
                        l = []
                        raw = [s['ad1'], s['ad2'], s['ad3']]
                        trigger = False
                        print(raw)
                        for v, ad in enumerate(raw):
                            if ad == None: 
                                if v == 0:
                                    l = None
                                    trigger = True
                                else: 
                                    l = raw[v-1]
                                    trigger = True
                            if trigger: break
                            if ad.isnumeric() and ad:
                                l.append(int(ad))
                            else: l.append(ad)
                        innerDict[int(k)] = l
                    dict[int(row)] = innerDict
                dictList.append(dict)
            
            else:
                for i in range(len(arr)):
                    s = arr.iloc[i]
                    dict[int(s['row'])] = str(s['ad1'])
                
                with open(r'C:\Users\david\Desktop\test.json', 'w') as file:
                    json.dump(dict, file, indent=4)
                dictList.append(dict)

        return dictList


if __name__ == '__main__':
    # self.exportDB = exportDB(os.path.join(self.path, 'global', 'export.db'))
    ex = exportDB(os.path.join(os.path.expanduser('~'), 'Atomizer Toolbox', 'global', 'presets', 'Test', 'database.db'))
    ex.DBtoDicts()