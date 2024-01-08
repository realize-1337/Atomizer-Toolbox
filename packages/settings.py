import json

class settings():
    def __init__(self, path) -> None:
        self.path = path
    
    def setup(self, default_settings:dict) -> None:
        try:
            with open(self.path, 'w') as file:
                json.dump(default_settings, file, indent=4)
        except: raise PermissionError
    
    def saveDict(self, newDict) -> None:
        try:
            with open(self.path, 'w') as file:
                json.dump(newDict, file, indent=4)
        except: raise FileNotFoundError

    def getCurrentDict(self) -> dict:
        try:
            with open(self.path, 'r') as file:
                dict = json.load(file)
            return dict
        except:
            raise FileNotFoundError
      
    def set(self, key:str, value:float|str|int|bool) -> None:
        dict = self.getCurrentDict()
        try:
            dict[key] = value
            self.saveDict(dict)
        except:
            raise KeyError

    def get(self, key:str) -> float|str|None:
        dict = self.getCurrentDict()
        try: 
            return dict[key]
        except:
            raise KeyError
        
