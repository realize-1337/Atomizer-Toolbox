LATEST_URL = r'https://github.com/realize-1337/Atomizer-Toolbox/releases/latest/download/release.zip'

import os
import sys
import zipfile
from PyQt6.QtWidgets import *
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, QEvent, QCoreApplication
import subprocess
import winreg
import shutil
import json
import winshell
from win32com.client import Dispatch
UI_FILE = 'installer\installer.ui'
PY_FILE = 'installer\installer.py'
# subprocess.run(['pyuic6', '-x', UI_FILE, '-o', PY_FILE])
from installer import Ui_Dialog as main
import requests
        

class UI(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = main()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('./assets/ATT_LOGO.ico'))
        self.setWindowTitle('Atomizer ToolBox Online Installer')
        self.initInstaller()
        self.running = False

    def initInstaller(self):
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText('Install')

        self.ui.buttonBox.accepted.disconnect()
        self.ui.buttonBox.accepted.connect(self.install)
        self.defaultFolder = os.path.join(self.get_default_install_folder(), 'Atomizer ToolBox')
        print(self.defaultFolder)
        self.ui.path.setText(self.defaultFolder)
        self.ui.path.installEventFilter(self)

    def get_default_install_folder(self):
        if sys.platform == 'win32':
            if 'PROGRAMFILES(X86)' in os.environ:
                return os.environ['PROGRAMFILES(X86)']
            else:
                return os.environ['PROGRAMFILES']
        else:
            raise OSError("This script is intended for Windows only.")
    
    def eventFilter(self, obj, event):
        if obj == self.ui.path and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                folder = QFileDialog.getExistingDirectory(self, "Select Directory", directory=self.get_default_install_folder())
                if folder:
                    self.ui.path.setText(folder)
        return super().eventFilter(obj, event)
        
    def alreadyInstalled(self) -> bool:
        res = QMessageBox.warning(self, 'Already installed', 'Atomizer ToolBox is already installed at the specified path. <br> Install anyway?', defaultButton=QMessageBox.StandardButton.Yes, buttons=QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            return True
        else: return False

    def checkInstalled(self) -> bool:
        if os.path.exists(self.ui.path.text()) and len(os.listdir(self.ui.path.text()))>0: 
            return True
        else: return False

    def download_file_with_progress(self, url, destination):
        response = requests.get(url, stream=True)

        # Check if the request was successful
        response.raise_for_status()

        # Get the total file size in bytes (if available)
        total_size = int(response.headers.get('content-length', 0))
        self.ui.pbar.setMaximum(total_size)
        self.ui.pbar.setValue(0)
        self.ui.pbar.setFormat('Downloading......%p%')

        # Create a progress bar using tqdm
        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    file.write(chunk)
                    self.ui.pbar.setValue(self.ui.pbar.value()+len(chunk))
                    QCoreApplication.processEvents()

    def install(self):
        '''
        Handles install process
        '''
        if self.checkInstalled():
            if self.alreadyInstalled() == False: 
                return

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ui.path.removeEventFilter(self)
        if not os.path.exists(self.ui.path.text()):
            os.mkdir(self.ui.path.text())
        
        zip_file_path = os.path.join(self.ui.path.text(), 'release.zip')
        self.download_file_with_progress(LATEST_URL, zip_file_path)
        
        self.ui.pbar.setFormat('Download complete. Unpacking download')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(zip_file_path)
                               )
        os.remove(zip_file_path)
        self.createRegistryKeys(self.ui.path.text())    
        self.ui.pbar.setFormat('Install complete. Cleanup done. Enjoy!')
        self.createShortCut(self.ui.desktopShortcut.isChecked(), self.ui.startmenuShortcut.isChecked())
        print('Installing')
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Abort).setText('Close')
        QMessageBox.information(self, 'Information', 'The first start of the Atomizer Toolbox might take up to a minute depending on the used hardware.')

    def createRegistryKeys(self, path):
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\AtomizerToolbox"

        appdata = os.path.join(os.getenv('LOCALAPPDATA'), 'AtomizerToolbox')
        if not os.path.exists(appdata):
            os.mkdir(appdata)
        uninstall = os.path.join(path, 'uninstall.exe')
        shutil.copy(uninstall, os.path.join(appdata, 'uninstall.exe'))
        uninstall = os.path.join(appdata, 'uninstall.exe')

        settings = {'path':path}
        loc = os.path.join(appdata, 'loc.json')
        with open(loc, 'w') as file:
            json.dump(settings, file, indent=4)

        icon = os.path.join(path, 'AtomizerToolbox.exe')
        version_loc = os.path.join(path, 'assets', 'versioninfo.json')
        with open(version_loc, 'r') as file:
            version = json.load(file)['currentVersion']
        try: 
            winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Atomizer Toolbox")
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "David Maerker")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, f"{version}")
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall)
            winreg.CloseKey(key)
        except Exception as e:
            print(f'Key {e} not saved!')
        print('Registry Done!')

    def createShortCut(self, desk_=False, start_=False):
        if desk_:
            desk = winshell.desktop()
            path = self.ui.path.text()
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(os.path.join(desk, 'Atomizer Toolbox.lnk'))
            shortcut.Targetpath = os.path.join(path, 'AtomizerToolbox.exe')
            shortcut.WorkingDirectory = path
            shortcut.IconLocation = os.path.join(path, 'AtomizerToolbox.exe')
            shortcut.save()
        if start_:
            start = winshell.start_menu()
            path = self.ui.path.text()
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(os.path.join(start, 'Atomizer Toolbox.lnk'))
            shortcut.Targetpath = os.path.join(path, 'AtomizerToolbox.exe')
            shortcut.WorkingDirectory = path
            shortcut.IconLocation = os.path.join(path, 'AtomizerToolbox.exe')
            shortcut.save()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = UI()
    window.show()
    sys.exit(app.exec())