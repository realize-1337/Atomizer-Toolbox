import os
import sys
import re
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

class DeleteDialog(QDialog):
    def __init__(self, items:list, path):
        super().__init__()
        self.items = items
        self.path = path
        self.initUI()
        
 
    def initUI(self):
        layout = QVBoxLayout()
        self.line_input = QLineEdit(self)
        self.box = QComboBox(self)
        self.box.addItem('Select Preset to delete')
        self.box.addItems(self.items)
        self.line_input.setPlaceholderText("Type 'YES' to confirm")
        layout.addWidget(self.box)
        layout.addWidget(self.line_input)

        self.line_input.setHidden(True)

        delete_Button = QPushButton('Delete', self)
        discard_button = QPushButton('Abort', self)

        discard_button.clicked.connect(self.discardClicked)
        delete_Button.clicked.connect(self.deleteClicked)
        delete_Button.setStyleSheet('background-color: red')
        layout.addWidget(delete_Button)
        layout.addWidget(discard_button)
        self.setLayout(layout)

    def doubleCheck(self) -> bool:
        self.line_input.setHidden(False)
        self.line_input.setPlaceholderText(f"Type '{self.box.currentText()}' to delete")
        input_text = f'{self.line_input.text()}'
        if input_text in [self.box.currentText(), f"\'{self.box.currentText()}\'", f'\"{self.box.currentText()}\"']:
            input_text = self.box.currentText()
            return (True, input_text)
        else: return (False, '')

    def deleteClicked(self):
        self.box.setDisabled(True)
        dc = self.doubleCheck()
        if dc[0]:
            response = QMessageBox.question(self, 'Are you sure?', f'This is permanent. Are you sure?')
            if response == QMessageBox.StandardButton.Yes:
                files = os.listdir(os.path.join(self.path, dc[1]))
                for file in files: os.remove(os.path.join(self.path, dc[1], file))
                os.rmdir(os.path.join(self.path, dc[1]))
                QMessageBox.information(self, 'Success', f'Successfully deleted preset {dc[1]}')
                self.accept()
        else:
            self.setEnabled(True)
       
    def discardClicked(self):
        self.reject()

class ColumnChanger(QDialog):
    def __init__(self, index, ui, col):
        super().__init__()
        self.index = index
        self.ui = ui
        self.col = col
        self.initUI()
        

    def initUI(self):
        layout = QVBoxLayout()

        self.line_input = QLineEdit(self)
        layout.addWidget(self.line_input)
        self.line_input.setPlaceholderText('Enter a custom Name')

        save_button = QPushButton('Save', self)
        discard_button = QPushButton('Discard', self)
        if self.col: delete_button = QPushButton('Delete Column', self)
        else: delete_button = QPushButton('Delete Row', self)

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

class SaveDialog(QDialog):
    def __init__(self, items:list, main):
        super().__init__()
        self.items = items
        self.transfer = main
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.line_input = QLineEdit(self)
        self.line_input.setPlaceholderText('Enter new preset name')
        self.cbox = QComboBox(self)
        self.cbox.addItem('or select already existing preset')
        self.cbox.currentIndexChanged.connect(self.updateLine)
        self.cbox.addItems(self.items)
        layout.addWidget(self.line_input)
        layout.addWidget(self.cbox)

        save_button = QPushButton('Save', self)
        discard_button = QPushButton('Abort', self)

        save_button.clicked.connect(self.saveClicked)
        discard_button.clicked.connect(self.discardClicked)

        layout.addWidget(save_button)
        layout.addWidget(discard_button)

        self.setLayout(layout)

    def updateLine(self):
        if self.cbox.currentText() != 'or select already existing preset':
            self.line_input.setText(self.cbox.currentText())

    def saveClicked(self):
        input_text = f'{self.line_input.text()}'
        pattern = r"^[^\\/:*?\"<>|]*$"
        if re.match(pattern, input_text) is not None:
            if input_text in self.items:
                response = QMessageBox.question(self, 'Overwrite', f'This preset already exists. Do you want to overwrite it?')
            else:
                response = QMessageBox.question(self, 'Save', f'Save as {input_text}?')
            
            if response == QMessageBox.StandardButton.Yes:
                self.transfer.exportName = input_text
                self.accept()
        else: 
            self.line_input.setText('')
            self.line_input.setPlaceholderText('Please enter a valid name')
       
    def discardClicked(self):
        self.transfer.exportName = None
        self.reject()

class CustomInputBox(QDialog):
    def __init__(self, cbox, app):
        super().__init__()
        self.initUI()
        self.cbox = cbox
        self.app = app

    def initUI(self):
        layout = QVBoxLayout()
        
        self.line_input = QLineEdit(self)
        layout.addWidget(self.line_input)

        save_button = QPushButton('Save', self)
        discard_button = QPushButton('Discard', self)

        save_button.clicked.connect(self.saveClicked)
        discard_button.clicked.connect(self.discardClicked)

        layout.addWidget(save_button)
        layout.addWidget(discard_button)

        self.setLayout(layout)

    def saveClicked(self):
        input_text = self.line_input.text()
        # self.cbox.setCurrentText(input_text)
        index = self.cbox.currentIndex()
        self.cbox.disconnect()
        self.cbox.setItemData(index, input_text)
        self.cbox.setItemData(index, input_text, 0)
        self.cbox.currentTextChanged.connect(partial(self.app.editbox, self.cbox))
        self.accept()

    def discardClicked(self):
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
        self.createLoadList()
        self.savedCheck = True

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

    def loadButtons(self):
        buttons = self.ui.buttonBox.buttons()
        print(buttons)
        for but in buttons:
            t = but.text()
            if t == 'Save':
                but.clicked.connect(self.save)
            if t == 'Open':
                but.setText('Delete')
                but.clicked.connect(self.deletePreset)
            if t == 'Close':
                but.clicked.connect(self.close)

    def addRow(self):
        row_count = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_count)
        col_count = self.ui.tableWidget.columnCount()
        for i in range(col_count):
            box = self.createCombobox()
            box.currentTextChanged.connect(partial(self.editbox, box))
            self.ui.tableWidget.setCellWidget(row_count, i, box)
        self.headers()
        self.savedCheck = False
       
    def addCol(self):
        col_count = self.ui.tableWidget.columnCount()
        self.ui.tableWidget.insertColumn(col_count)
        row_count = self.ui.tableWidget.rowCount()
        for i in range(row_count):
            box = self.createCombobox()
            box.currentTextChanged.connect(partial(self.editbox, box))
            self.ui.tableWidget.setCellWidget(i, col_count, box)
        self.headers()
        self.savedCheck = False
    
    def createCombobox(self):
        dfs = {}
        box = QComboBox()
        for item in os.listdir(self.sharePath):
            with open(os.path.join(self.sharePath, item), 'r') as file:
                name_ = item[:-11]
                dfs[name_] = pd.read_json(file)
                dict = dfs[name_].to_dict()
            for k, v in dict.items():
                name = f'{k}'
                if len(v) > 1:
                    for key, value in v.items():
                        nameK = f'{name} : {key}'
                        box.addItem(nameK, [name_, k, key])
                else: box.addItem(name, [name_, k, 0])
        box.addItem('NULL', None)
        box.addItem('Custom Input', '')
        return box

    def editbox(self, cbox):
        self.savedCheck = False
        if type(cbox.currentData()) == str:
            print('Change')
            dialog = CustomInputBox(cbox, self)
            dialog.setWindowTitle(f'Enter custom Input')
            dialog.exec()

    def save(self):
        self.exportName = None
        dict = {}
        vheader = {}
        hheader = {}
        for row in range(self.ui.tableWidget.rowCount()):
            innerDict = {}
            try: vheader[row] = self.ui.tableWidget.verticalHeaderItem(row).text()
            except: vheader[row] = f'{row+1}'
            for col in range(self.ui.tableWidget.columnCount()):
                cbox = self.ui.tableWidget.cellWidget(row, col)
                innerDict[col] = cbox.currentData()
                try: hheader[col] = self.ui.tableWidget.horizontalHeaderItem(col).text()
                except: hheader[col] = f'{col+1}'
            dict[row] = innerDict

        print(dict)
        print(vheader)
        print(hheader)
        self.exportName = ''
        items = os.listdir(self.PresetPath)
        print(items)
        dialog = SaveDialog(items, self)
        dialog.setWindowTitle(f'Enter custom Input')
        dialog.exec()

        if self.exportName:
            exportPath = os.path.join(self.PresetPath, self.exportName)
            if not os.path.exists(exportPath):
                os.mkdir(exportPath)
            
            dicts = [(dict, '0_items'), (hheader, '1_hheader'), (vheader, '2_vheader')]
            for dict in dicts:
                with open(os.path.join(exportPath, f"{dict[1]}.json"), 'w+') as file:
                    json.dump(dict[0], file)
            print('Export Done!')
            self.savedCheck = True
            self.createLoadList()

    def load(self):
        print('Loading...')
        if self.ui.comboBox.currentText() != 'Optional: Select existing preset to edit':
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.setColumnCount(0)
            path = os.path.join(self.PresetPath, self.ui.comboBox.currentText())
            items = os.listdir(path)
            dicts = []
            for item in items:
                with open(os.path.join(path, item), 'r') as file:
                    dicts.append(json.load(file))

            for i in range(len(dicts[1])):
                self.addCol()
            for i in range(len(dicts[2])):
                self.addRow()
            
            hheader = []
            for k,v in dicts[1].items():
                hheader.append(v)
            self.ui.tableWidget.setHorizontalHeaderLabels(hheader)
            vheader = []
            for k,v in dicts[2].items():
                vheader.append(v)
            self.ui.tableWidget.setVerticalHeaderLabels(vheader)

            for key, value in dicts[0].items():
                for k, v in value.items():
                    box = self.ui.tableWidget.cellWidget(int(key), int(k))
                    if type(v) != str:
                        index = box.findData(v)
                        if index != -1:
                            box.setCurrentIndex(index)
                        else: box.setCurrentIndex(-2)
                    else: 
                        box.disconnect()
                        index = self.createCombobox().count()-1
                        box.setCurrentIndex(index)
                        box.setItemData(index, v)
                        box.setItemData(index, v, 0)
                        box.currentTextChanged.connect(partial(self.editbox, box))
            
            self.savedCheck = True
                           
    def createLoadList(self):
        try: self.ui.comboBox.disconnect()
        except: pass
        self.ui.comboBox.clear()
        self.ui.comboBox.addItem('Optional: Select existing preset to edit')
        items = os.listdir(self.PresetPath)
        self.ui.comboBox.addItems(items)
        self.ui.comboBox.currentTextChanged.connect(self.load)

    def closeEvent(self, event):
        print('Closing...')
        if not self.savedCheck:
            response = QMessageBox.question(self, 'Quit without saving?', f'Are you sure you want to quit without saving changes?')
            if response == QMessageBox.StandardButton.Yes:
                self.close()
            else: event.ignore()
        else: event.accept()

    def deletePreset(self):
        items = os.listdir(self.PresetPath)
        dialog = DeleteDialog(items, self.PresetPath)
        dialog.setWindowTitle(f'Delete Presets')
        dialog.exec()


def call():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    #Dialog = QtWidgets.QDialog()
    ui = UI(app)
    ui.show()
    app.exec()
    sys.exit(app.exec())

def callInside():
    app = QtWidgets.QApplication(sys.argv)
    ui = UI(app)
    ui.exec()

if __name__ == '__main__':
    call()