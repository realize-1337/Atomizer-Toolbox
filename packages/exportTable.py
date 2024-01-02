import os
import sys
import re
import copy
currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
sys.path.append(parentDir)
import subprocess
from packages.exportDB import exportDB
from functools import partial
import json
import pandas as pd
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
# UI_FILE = './GUI/tableExport.ui'
# PY_FILE = './GUI/tableExport.py'
# subprocess.run(['pyuic6', '-x', UI_FILE, '-o', PY_FILE])
from GUI.tableExport import Ui_Dialog as main

class DeleteDialog(QDialog):
    def __init__(self, items:list, path, main):
        super().__init__()
        self.items = items
        self.path = path
        self.main = main
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
                self.main.createLoadList()
                self.main.ui.tableWidget.clear()
                self.main.ui.tableWidget.setRowCount(0)
                self.main.ui.tableWidget.setColumnCount(0)
                self.accept()
        else:
            self.setEnabled(True)
       
    def discardClicked(self):
        self.reject()

class ColumnChanger(QDialog):
    def __init__(self, index, ui:QTableWidget, col:bool, main:QDialog):
        super().__init__()
        self.index = index
        self.ui = ui
        self.col = col
        self.main = main
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
        innerLayout = QHBoxLayout()
        if self.col:
            text_1 = 'Move Left'
            text_2 = 'Move Right'
        else: 
            text_1 = 'Move Up'
            text_2 = 'Move Down'
        self.left_up_button = QPushButton(text_1, self)
        self.left_up_button.clicked.connect(partial(self.move, -1))
        self.right_down_button = QPushButton(text_2, self)
        self.right_down_button.clicked.connect(partial(self.move, 1))
        innerLayout.addWidget(self.left_up_button)
        innerLayout.addWidget(self.right_down_button)

        self.checkBorders()

        layout.addLayout(innerLayout)
        self.setLayout(layout)

    def checkBorders(self):
        if self.index == 0: self.left_up_button.setDisabled(True)
        else: self.left_up_button.setEnabled(True)

        if self.col: 
            trigger = bool(self.index == self.ui.columnCount()-1)
            self.line_input.setText(self.ui.horizontalHeaderItem(self.index).text())
        else: 
            trigger = bool(self.index == self.ui.rowCount()-1)
            self.line_input.setText(self.ui.verticalHeaderItem(self.index).text())

        if trigger: self.right_down_button.setDisabled(True)
        else: self.right_down_button.setEnabled(True)

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

    def move(self, dir:int):
        if self.col:
            print('Col')
            target = self.index + dir
            
            header_index:QTableWidgetItem = self.ui.horizontalHeaderItem(self.index).clone()
            header_target:QTableWidgetItem = self.ui.horizontalHeaderItem(target).clone()
            
            self.ui.setHorizontalHeaderItem(target, header_index)
            self.ui.setHorizontalHeaderItem(self.index, header_target)

            for i in range(self.ui.rowCount()):
                box_index:QComboBox = self.ui.cellWidget(i, self.index)
                box_target:QComboBox = self.ui.cellWidget(i, target)
                box_index.disconnect()
                box_target.disconnect()
                index_index = box_index.currentIndex()
                index_target = box_index.currentIndex()
                text_index = box_index.currentText()
                text_target = box_target.currentText()
                customtext_index = box_index.itemText(box_index.count()-1)
                customtext_target = box_target.itemText(box_target.count()-1)
                customdata_index = box_index.itemData(box_index.count()-1)
                customdata_target = box_target.itemData(box_target.count()-1)
                box_index.removeItem(box_index.count()-1)
                box_target.removeItem(box_target.count()-1)
                box_index.addItem(f'{customtext_target}', customdata_target)
                box_target.addItem(f'{customtext_index}', customdata_index)
                box_target.setCurrentIndex(index_index)
                box_target.setCurrentText(text_index)
                box_index.setCurrentIndex(index_target)
                box_index.setCurrentText(text_target)
                box_index.currentTextChanged.connect(partial(self.main.editbox, box_index))
                box_target.currentTextChanged.connect(partial(self.main.editbox, box_target))
            self.index = target
            self.checkBorders()
            print(f'Done: New Index {self.index}')
        else:
            print('Row')
            target = self.index + dir
            colCount = self.ui.columnCount()

            header_index:QTableWidgetItem = self.ui.verticalHeaderItem(self.index).clone()
            header_target:QTableWidgetItem = self.ui.verticalHeaderItem(target).clone()
            
            self.ui.setVerticalHeaderItem(target, header_index)
            self.ui.setVerticalHeaderItem(self.index, header_target)

            for i in range(colCount):
                box_index:QComboBox = self.ui.cellWidget(self.index, i)
                box_target:QComboBox = self.ui.cellWidget(target, i)
                box_index.disconnect()
                box_target.disconnect()
                index_index = box_index.currentIndex()
                index_target = box_index.currentIndex()
                text_index = box_index.currentText()
                text_target = box_target.currentText()
                customtext_index = box_index.itemText(box_index.count()-1)
                customtext_target = box_target.itemText(box_target.count()-1)
                customdata_index = box_index.itemData(box_index.count()-1)
                customdata_target = box_target.itemData(box_target.count()-1)
                box_index.removeItem(box_index.count()-1)
                box_target.removeItem(box_target.count()-1)
                box_index.addItem(f'{customtext_target}', customdata_target)
                box_target.addItem(f'{customtext_index}', customdata_index)
                box_target.setCurrentIndex(index_index)
                box_target.setCurrentText(text_index)
                box_index.setCurrentIndex(index_target)
                box_index.setCurrentText(text_target)
                box_index.currentTextChanged.connect(partial(self.main.editbox, box_index))
                box_target.currentTextChanged.connect(partial(self.main.editbox, box_target))
            self.index = target
            self.checkBorders()
            print(f'Done: New Index {self.index}')

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
        self.setWindowIcon(QtGui.QIcon('assets/ATT_LOGO.ico'))
        
    def headers(self):
        try: self.ui.tableWidget.horizontalHeader().sectionDoubleClicked.disconnect()
        except: pass
        try: self.ui.tableWidget.verticalHeader().sectionDoubleClicked.disconnect()
        except: pass
        self.ui.tableWidget.horizontalHeader().sectionDoubleClicked.connect(self.changeHeader)
        self.ui.tableWidget.verticalHeader().sectionDoubleClicked.connect(self.changeVHeader)
        
    def changeHeader(self, index):
        dialog = ColumnChanger(index, self.ui.tableWidget, col=True, main=self)
        dialog.setWindowTitle(f'Edit Column {index+1}')
        dialog.exec()
        
    def changeVHeader(self, index):
        dialog = ColumnChanger(index, self.ui.tableWidget, col=False, main=self)
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
            if t == 'Save All':
                but.setText('Clear')
                but.clicked.connect(self.clear)

    def addRow(self):
        row_count = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_count)
        col_count = self.ui.tableWidget.columnCount()
        for i in range(col_count):
            box = self.createCombobox()
            box.currentTextChanged.connect(partial(self.editbox, box))
            self.ui.tableWidget.setCellWidget(row_count, i, box)
        self.ui.tableWidget.setVerticalHeaderItem(row_count, QTableWidgetItem(f'{row_count+1}'))
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
        self.ui.tableWidget.setHorizontalHeaderItem(col_count, QTableWidgetItem(f'{col_count+1}'))
        self.headers()
        self.savedCheck = False
    
    def createCombobox(self):
        dfs = {}
        box = QComboBox()
        ex = exportDB(os.path.join(os.path.expanduser('~'), 'Atomizer Toolbox', 'global', 'export.db'))
        full = ex.readExportOption()
        for dict, name_ in full:
            for k, v in dict.items():
                name = f'{k}'
                if len(v) > 1:
                    for key, value in v.items():
                        nameK = f'{name} : {key}'
                        box.addItem(nameK, [name_, k, key])
                else: box.addItem(name, [name_, k, 0])
            box.insertSeparator(99999)
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
            ex = exportDB(os.path.join(exportPath, 'database.db'))
            for dict in dicts:
                ex.writeExport(dict[0], dict[1])
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
        dialog = DeleteDialog(items, self.PresetPath, main=self)
        dialog.setWindowTitle(f'Delete Presets')
        dialog.exec()

    def clear(self):
        if not self.savedCheck:
            response = QMessageBox.question(self, 'Are you sure', 'Do you really want to clear the table without saving?')
            if response == QMessageBox.StandardButton.Yes:
                self.ui.tableWidget.clear()
                self.ui.tableWidget.setRowCount(0)
                self.ui.tableWidget.setColumnCount(0)
        else: 
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.setColumnCount(0)

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