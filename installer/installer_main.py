LATEST_URL = r'https://github.com/realize-1337/Atomizer-Toolbox/releases/latest/download/release.zip'

import os
import sys
import zipfile
from PyQt6.QtWidgets import *
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, QEvent, QCoreApplication
import subprocess
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
            
        if not os.path.exists(self.ui.path.text()):
            os.mkdir(self.ui.path.text())
        
        zip_file_path = os.path.join(self.ui.path.text(), 'release.zip')
        self.download_file_with_progress(LATEST_URL, zip_file_path)
        
        self.ui.pbar.setFormat('Download complete. Unpacking download')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(zip_file_path)
                               )
        os.remove(zip_file_path)    
        self.ui.pbar.setFormat('Install complete. Cleanup done. Enjoy!')
        print('Installing')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = UI()
    window.show()
    sys.exit(app.exec())