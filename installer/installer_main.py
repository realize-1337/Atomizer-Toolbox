LATEST_URL = r'https://gitlab.kit.edu/uuyqx/Atomizer-Toolbox/-/raw/be07017afca37614b15a9fadd5fec45630c879e3/release.zip?inline=false'
TAG_NAME = '1.69'
LATEST_SC = f'https://gitlab.kit.edu/uuyqx/Atomizer-Toolbox/-/archive/{TAG_NAME}/Atomizer-Toolbox-{TAG_NAME}.zip'

import os
import sys
import zipfile
from PyQt6.QtWidgets import *
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, QEvent, QCoreApplication, QRunnable, pyqtSignal, QObject, QThreadPool, QProcess, QTextStream
import subprocess
import winreg
import shutil
import json
import winshell
from win32com.client import Dispatch
import ctypes
from subprocess import Popen, run
UI_FILE = 'installer\installer.ui'
PY_FILE = 'installer\installer.py'
# subprocess.run(['pyuic6', '-x', UI_FILE, '-o', PY_FILE])
from installer import Ui_Dialog as main
import requests

class WorkerSignals(QObject):
    finished = pyqtSignal() 

class Worker(QRunnable):
    def __init__(self, path):
        super().__init__()
        self.signals = WorkerSignals()
        self.path = path

    def run(self):
        subprocess.run(self.path)
        self.signals.finished.emit()        

class UI(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = main()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('./assets/ATT_LOGO.ico'))
        self.setWindowTitle('Atomizer ToolBox Online Installer')
        self.initInstaller()
        self.running = False
        print(sys.executable)
        # self.ui.output_textedit.setVisible(False)

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.read_output)
        # self.process.finished.connect(self.compileComplete)
        
    def initInstaller(self):
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText('Install')
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Save).setText('Compile')

        self.ui.buttonBox.accepted.disconnect()
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Save).disconnect()
        self.ui.buttonBox.accepted.connect(self.install)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Save).clicked.connect(self.compile)
        self.defaultFolder = os.path.join(self.get_default_install_folder(), 'Atomizer ToolBox')
        print(self.defaultFolder)
        return_code = subprocess.call(["python", "--version"])
        if return_code == 0: self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Save).setEnabled(True)
        else: self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Save).setEnabled(False)
        self.ui.path.setText(self.defaultFolder)
        self.ui.path.installEventFilter(self)
        try:
            admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            admin = False
        if not admin:
            QMessageBox.information(self, 'Information', 'Your are not running as Admin. <br> This might cause issues if you don\'t have priviliges to write to the install folder. <br> Make sure to select a valid folder or run again as admin.')

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
                    if len(os.listdir(folder)) > 0 and (not 'setup.py' in os.listdir(folder) or not 'assets' in os.listdir(folder)) :
                        folder = os.path.join(folder, 'Atomizer Toolbox')
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
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Save).setEnabled(False)
        self.ui.path.removeEventFilter(self)
        if not os.path.exists(self.ui.path.text()):
            os.mkdir(self.ui.path.text())
        
        zip_file_path = os.path.join(self.ui.path.text(), 'release.zip')
        self.download_file_with_progress(LATEST_URL, zip_file_path)
        
        self.ui.pbar.setFormat('Download complete. Unpacking download')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(zip_file_path))
            files = zip_ref.namelist()
        os.remove(zip_file_path)
        self.createRegistryKeys(self.ui.path.text(), files)    
        self.ui.pbar.setFormat('Install complete. Cleanup done. Enjoy!')
        self.createShortCut(self.ui.desktopShortcut.isChecked(), self.ui.startmenuShortcut.isChecked())
        print('Installing')
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Abort).setText('Close')
        QMessageBox.information(self, 'Information', 'The first start of the Atomizer Toolbox might take up to a minute depending on the used hardware.')

    def createRegistryKeys(self, path, files=None):
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\AtomizerToolbox"

        appdata = os.path.join(os.getenv('LOCALAPPDATA'), 'AtomizerToolbox')
        if not os.path.exists(appdata):
            os.mkdir(appdata)
        uninstall = os.path.join(path, 'uninstall.exe')
        shutil.copy(uninstall, os.path.join(appdata, 'uninstall.exe'))
        uninstall = os.path.join(appdata, 'uninstall.exe')

        settings = {'path':path, 
                    'files':files}
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

    def compile(self):
        if self.checkInstalled():
            if self.alreadyInstalled() == False: 
                return

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Save).setEnabled(False)
        self.ui.path.removeEventFilter(self)
        if not os.path.exists(self.ui.path.text()):
            os.mkdir(self.ui.path.text())
        # response = requests.get(LATEST_SC)
        # release_info = response.json()

        # tag_name = release_info['tag_name']
        # https://gitlab.kit.edu/uuyqx/Atomizer-Toolbox/-/archive/1.69/Atomizer-Toolbox-1.69.zip
        # zip_url = rf"https://gitlab.kit.edu/uuyqx/Atomizer-Toolbox/-/archive/{tag_name}.zip"
        # zip_url = rf"https://gitlab.kit.edu/uuyqx/Atomizer-Toolbox/-/archive/{tag_name}.zip"
        zip_file_path = os.path.join(self.ui.path.text(), 'source.zip')

        self.download_file_with_progress(LATEST_SC, zip_file_path)
        self.ui.pbar.setMaximum(100)
        self.ui.pbar.setValue(100)
        self.ui.pbar.setFormat('Download complete. Unpacking download')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(zip_file_path)
                               )
        os.remove(zip_file_path)
        folder = os.path.join(self.ui.path.text(), f'Atomizer-Toolbox-{TAG_NAME}')
        
        self.ui.pbar.setMaximum(100)
        self.ui.pbar.setValue(100)
        self.ui.pbar.setFormat('Compile in progress. This will take a while. You can track the progress in the command window.')
        self.base_folder = folder
        print(folder)
        self.ui.output_textedit.setVisible(True)
        # self.venv_activate_script = os.path.join(self.base_folder, "venv", "Scripts", "activate") if sys.platform == "win32" else os.path.join(self.base_folder, "venv", "bin", "activate")
        self.create_venv()
        # self.install_requirements()
        # self.run_script()
        # if self.ui.matlab.isChecked():
        #     print('Installing with matlab')
        #     self.run_batch_file(os.path.join(folder, "setup.bat"))
        # else: 
        #     self.run_batch_file(os.path.join(folder, 'setup_no_matlab.bat'))
        # self.run_command()
                
    def compileComplete(self):
        self.ui.pbar.setMaximum(100)
        self.ui.pbar.setValue(100)
        self.ui.pbar.setFormat('Compile in completed.')
        folder = os.path.join(self.ui.path.text(), f'Atomizer-Toolbox-{TAG_NAME}')
        shutil.copytree(os.path.join(folder, 'AtomizerToolbox'), os.path.dirname(folder), dirs_exist_ok=True)
        files = os.listdir(os.path.join(folder, 'AtomizerToolbox'))
        shutil.rmtree(folder)
        self.createRegistryKeys(self.ui.path.text(), files)    
        self.ui.pbar.setFormat('Install complete. Cleanup done. Enjoy!')
        self.createShortCut(self.ui.desktopShortcut.isChecked(), self.ui.startmenuShortcut.isChecked())
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Abort).setText('Close')
        QMessageBox.information(self, 'Information', 'The first start of the Atomizer Toolbox might take up to a minute depending on the used hardware.')

    def run_batch_file(self, path):
        self.ui.output_textedit.setVisible(True)
        try:
            self.process.setWorkingDirectory(os.path.dirname(path))
            self.process.start("cmd.exe", ["/c", path])
            self.ui.output_textedit.clear()
        except:
            pass

    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        self.ui.output_textedit.insertPlainText(output)
        print(output)
        self.ui.output_textedit.verticalScrollBar().setValue(self.ui.output_textedit.verticalScrollBar().maximum())

    def create_venv(self):
        print('VENV')
        self.process.finished.connect(self.install_requirements)
        self.process.setWorkingDirectory(os.path.dirname(self.base_folder))
        self.process.start("python", [f"-m", "venv", f"{self.base_folder}\\venv"])
        # cmd.exe python -m venv "C:\Users\david\Desktop\test\venv"
        # self.ui.output_textedit.insertPlainText(10*"***Virtual Environment created***\n")
        # subprocess.run([sys.executable, "-m", "venv", "venv"])

    def install_requirements(self):
        print('REQ')
        # subprocess.run([f"{self.base_folder}\\venv\\Scripts\\pip", "install", "-r", f"{self.base_folder}\\requirements.txt"])
        self.process.finished.disconnect()
        self.process.finished.connect(self.run_script)
        self.process.start(f"{self.base_folder}\\venv\\Scripts\\pip.exe", ["/c", "-m", "venv", f"{self.base_folder}\\venv"])

    def run_script(self):
        print('SETUP')
        self.process.finished.disconnect()
        self.process.finished.connect(self.compileComplete)
        subprocess.run([f"{self.base_folder}\\venv\\Scripts\\python", f"{self.base_folder}\\setup.py"])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = UI()
    window.show()
    sys.exit(app.exec())