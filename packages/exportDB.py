import os
import sqlite3
import pandas as pd

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
                    else: a1, a2, a3 = l
                    
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
                    innerDict[row] = row[i]
                dict[col[1]] = innerDict
            dictList.append((dict, table_name))

            return dictList