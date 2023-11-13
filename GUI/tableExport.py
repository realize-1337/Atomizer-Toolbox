# Form implementation generated from reading ui file './GUI/tableExport.ui'
#
# Created by: PyQt6 UI code generator 6.6.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1068, 580)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(parent=Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.addCol = QtWidgets.QPushButton(parent=self.tab)
        self.addCol.setObjectName("addCol")
        self.verticalLayout.addWidget(self.addCol)
        self.addRow = QtWidgets.QPushButton(parent=self.tab)
        self.addRow.setObjectName("addRow")
        self.verticalLayout.addWidget(self.addRow)
        self.gridLayout_3.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(parent=self.tab)
        self.tableWidget.setDragEnabled(False)
        self.tableWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragOnly)
        self.tableWidget.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setObjectName("tableWidget")
        self.gridLayout_3.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox = QtWidgets.QComboBox(parent=self.tab)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=self.tab)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Close|QtWidgets.QDialogButtonBox.StandardButton.Open|QtWidgets.QDialogButtonBox.StandardButton.Save|QtWidgets.QDialogButtonBox.StandardButton.SaveAll)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout_4.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Export Tables"))
        self.addCol.setText(_translate("Dialog", "Add Column"))
        self.addRow.setText(_translate("Dialog", "Add Row"))
        self.buttonBox.setToolTip(_translate("Dialog", "<html><head/><body><p>Open - Load File from Dropdown</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "Tab 1"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())