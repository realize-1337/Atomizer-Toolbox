import os
import sys

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
sys.path.append(parentDir)
import subprocess
import json
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
# UI_FILE = './GUI/bulkExport.ui'
# PY_FILE = './GUI/bulkExport.py'
# subprocess.run(['pyuic6', '-x', UI_FILE, '-o', PY_FILE])
from GUI.bulkExport import Ui_Dialog as main

class UI(QDialog):
    def __init__(self, app):
        super().__init__()
        self.ui = main()
        self.ui.setupUi(self)
        self.app = app
        self.loadButtons()
        self.path = os.path.join(os.path.expanduser('~'), 'Atomizer Toolbox', 'global', 'export')
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.loadValues()
        self.exportPath = None
        self.ui.CreateFile.clicked.connect(self.selectFolder)
        self.ui.ChoseFile.clicked.connect(self.selectFile)


    def loadButtons(self):
        buttons = self.ui.buttonBox.buttons()
        for but in buttons:
            t = but.text()
            if t == 'OK':
                but.clicked.connect(self.send)
                but.setText('Save')

    def loadValues(self):
        if not os.path.exists(os.path.join(self.path, 'bulk.json')): return
        with open(os.path.join(self.path, 'bulk.json'), 'r') as file:
            data = json.load(file)
        self.ui.innerLine.setText('; '.join(str(x) for x in data['inner']).replace('.', ','))
        self.ui.middleLine.setText('; '.join(str(x) for x in data['middle']).replace('.', ','))
        self.ui.outerLine.setText('; '.join(str(x) for x in data['outer']).replace('.', ','))
        self.ui.innerUnit.setCurrentText(data['innerUnit'])
        self.ui.middleUnit.setCurrentText(data['middleUnit'])
        self.ui.outerUnit.setCurrentText(data['outerUnit'])
        try: 
            self.ui.currentFile.setText(data['export'].replace('/', '\\'))
            self.exportPath = data['export']
        except: self.ui.currentFile.setText('Please select file or folder')
        

    def send(self):
        inner = self.ui.innerLine.text()
        inner_ = inner.replace(',', '.')
        inner = inner_.split(';')
        innerList = [float(x) for x in inner]

        middle = self.ui.middleLine.text()
        middle_ = middle.replace(',', '.')
        middle = middle_.split(';')
        middleList = [float(x) for x in middle]
        
        outer = self.ui.outerLine.text()
        outer_ = outer.replace(',', '.')
        outer = outer_.split(';')
        outerList = [float(x) for x in outer]

        data = {
            'inner': innerList,
            'innerUnit': self.ui.innerUnit.currentText(),
            'middle': middleList,
            'middleUnit': self.ui.middleUnit.currentText(),
            'outer': outerList,
            'outerUnit': self.ui.outerUnit.currentText(),
            'export': self.exportPath
        }

        with open(os.path.join(self.path, 'bulk.json'), 'w') as file:
            json.dump(data, file)

    def selectFolder(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.exportPath = os.path.join(folder, 'export.xlsx')
        self.ui.currentFile.setText(self.exportPath.replace('/', '\\'))
    
    def selectFile(self):
        filename, null = QFileDialog.getOpenFileName(self, filter='*.xlsx', options=QFileDialog.Option.ReadOnly)
        if not filename.endswith('.xlsx'): return
        self.exportPath = filename
        self.ui.currentFile.setText(self.exportPath.replace('/', '\\'))
        

def call():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    #Dialog = QtWidgets.QDialog()
    ui = UI(app)
    ui.show()
    app.exec()
    sys.exit(app.exec())

if __name__ == '__main__':
    call()