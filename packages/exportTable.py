import os
import sys
currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
sys.path.append(parentDir)
import subprocess
from functools import partial
import json
import pandas as pd
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject

UI_FILE = './GUI/tableExport.ui'
PY_FILE = './GUI/tableExport.py'
subprocess.run(['pyuic6', '-x', UI_FILE, '-o', PY_FILE])
from GUI.tableExport import Ui_Dialog as main

class ColumnChanger(QDialog):
    def __init__(self, index, ui, col):
        super().__init__()
        self.initUI()
        self.index = index
        self.ui = ui
        self.col = col

    def initUI(self):
        layout = QVBoxLayout()

        self.line_input = QLineEdit(self)
        layout.addWidget(self.line_input)

        save_button = QPushButton('Save', self)
        discard_button = QPushButton('Discard', self)
        delete_button = QPushButton('Delete', self)

        save_button.clicked.connect(self.saveClicked)
        discard_button.clicked.connect(self.discardClicked)
        delete_button.clicked.connect(self.deleteClicked)

        layout.addWidget(save_button)
        layout.addWidget(discard_button)
        layout.addWidget(delete_button)

        self.setLayout(layout)

    def saveClicked(self):
        input_text = self.line_input.text()
        item = QTableWidgetItem(input_text)
        if self.col:
            self.ui.setHorizontalHeaderItem(self.index, item)
        else: self.ui.setVerticalHeaderItem(self.index, item)
        self.accept()

    def discardClicked(self):
        self.reject()

    def deleteClicked(self):
        response = QMessageBox.question(self, 'Delete', f'Delete?')
        if response == QMessageBox.StandardButton.Yes:
            if self.col:
                self.ui.removeColumn(self.index)
            else: self.ui.removeRow(self.index)
            self.reject()

class UI(QDialog):
    def __init__(self, app):
        super().__init__()
        self.ui = main()
        self.ui.setupUi(self)
        self.app = app

        self.sharePath = os.path.join(os.path.expanduser('~'), 'Atomizer Toolbox', 'global', 'share')
        self.PresetPath = os.path.join(os.path.expanduser('~'), 'Atomizer Toolbox', 'global', 'presets')

        self.ui.addCol.clicked.connect(self.addCol)
        self.ui.addRow.clicked.connect(self.addRow)
        self.headers()
        self.loadButtons()

    def headers(self):
        try: self.ui.tableWidget.horizontalHeader().sectionDoubleClicked.disconnect()
        except: pass
        try: self.ui.tableWidget.verticalHeader().sectionDoubleClicked.disconnect()
        except: pass
        self.ui.tableWidget.horizontalHeader().sectionDoubleClicked.connect(self.changeHeader)
        self.ui.tableWidget.verticalHeader().sectionDoubleClicked.connect(self.changeVHeader)
        
    def changeHeader(self, index):
        dialog = ColumnChanger(index, self.ui.tableWidget, col=True)
        dialog.setWindowTitle(f'Edit Column {index+1}')
        dialog.exec()
        
    def changeVHeader(self, index):
        dialog = ColumnChanger(index, self.ui.tableWidget, col=False)
        dialog.setWindowTitle(f'Edit Row {index+1}')
        dialog.exec()
        # app.exec()
        
    def headerContext(self, index):
        print('Context')
        headerItem = self.ui.tableWidget.horizontalHeaderItem(index)
        menu = QMenu(self)
        menu.addAction('delete')
        menu.exec()

        def delete():
            self.ui.tableWidget.removeColumn(index)

    def newClickEvent(self, event):
        print('Event')
        if event.button() == QtGui.QMouseEvent.LeftButton:
            print("Left Button Clicked")
        elif event.button() == QtGui.QMouseEvent.RightButton:
            #do what you want here
            print("Right Button Clicked")

    def loadButtons(self):
        buttons = self.ui.buttonBox.buttons()
        print(buttons)
        for but in buttons:
            t = but.text()
            if t == 'Save':
                but.clicked.connect(self.save)
            if t == 'Open':
                but.setText('Load')
                but.clicked.connect(self.load)
            if t == 'Close':
                but.clicked.connect(self.close_)

    def addRow(self):
        item = QTableWidgetItem('Test')
        row_count = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_count)
        col_count = self.ui.tableWidget.columnCount()
        for i in range(col_count):
            box = self.createCombobox()
            box.currentTextChanged.connect(partial(self.push, box))
            self.ui.tableWidget.setCellWidget(row_count, i, box)
        self.headers()
       
    def addCol(self):
        col_count = self.ui.tableWidget.columnCount()
        self.ui.tableWidget.insertColumn(col_count)
        row_count = self.ui.tableWidget.rowCount()
        for i in range(row_count):
            box = self.createCombobox()
            box.currentTextChanged.connect(partial(self.push, box))
            self.ui.tableWidget.setCellWidget(i, col_count, box)
        self.headers()
    
    def createCombobox(self):
        dfs = {}
        box = QComboBox()
        for item in os.listdir(self.sharePath):
            with open(os.path.join(self.sharePath, item), 'r') as file:
                name_ = item[:-11]
                dfs[name_] = pd.read_json(file)
                dict = dfs[name_].to_dict()
            for k, v in dict.items():
                name = f'{name_}: {k}'
                if len(v) > 1:
                    for key, value in v.items():
                        nameK = f'{name} : {key}'
                        box.addItem(nameK, [name_, k, key])
                else: box.addItem(name, [name_, k, 0])
        box.addItem('NULL', None)
        return box

    def push(self, cbox):
        print(cbox.currentData())

    def save(self):
        dict = {}
        i = 0
        for row in range(self.ui.tableWidget.rowCount()):
            innerDict = {} 
            for col in range(self.ui.tableWidget.columnCount()):
                cbox = self.ui.tableWidget.cellWidget(row, col)
                innerDict[col] = cbox.currentData()
            dict[row] = innerDict

        print(dict)

    def load(self):
        print('Loading...')

    def close_(self):
        print('Closing...')
        self.close()
        

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