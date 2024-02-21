import os
import sys
import winreg
import shutil
import json
        

def deleteKeys():
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\AtomizerToolbox"
    try: 
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        winreg.CloseKey(key)
    except Exception as e:
        print(f'Key {e} not deleted!')
    print('Registry Done!')

def removeInstall():
    loc = os.path.join(os.getenv('LOCALAPPDATA'), 'AtomizerToolbox', 'loc.json')
    with open(loc, 'r') as file:
        dict = json.load(file)
    dir = dict['path']
    files = dict['files']
    input('Press Enter to continue ...')
    for file in files[::-1]:
        shutil.rmtree(file, ignore_errors=True)


if __name__ == '__main__':
    print('Starting uninstall')
    removeInstall()
    print('Software removed')
    deleteKeys()
    print('Registry cleaned')
    print('Thanks for using Atomizer Toolbox')
    print('Info: Configuration files are not deleted and remain in your Userfiles')
    input('Press Enter to exit')
    sys.exit(0)