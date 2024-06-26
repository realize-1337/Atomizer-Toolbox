# Form implementation generated from reading ui file 'installer\installer.ui'
#
# Created by: PyQt6 UI code generator 6.6.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(578, 311)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Abort|QtWidgets.QDialogButtonBox.StandardButton.Help|QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 3)
        self.label = QtWidgets.QLabel(parent=Dialog)
        self.label.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        self.path = QtWidgets.QLineEdit(parent=Dialog)
        self.path.setReadOnly(True)
        self.path.setObjectName("path")
        self.gridLayout.addWidget(self.path, 1, 1, 1, 2)
        self.label_2 = QtWidgets.QLabel(parent=Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.pbar = QtWidgets.QProgressBar(parent=Dialog)
        self.pbar.setProperty("value", 0)
        self.pbar.setObjectName("pbar")
        self.gridLayout.addWidget(self.pbar, 4, 0, 1, 3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.desktopShortcut = QtWidgets.QCheckBox(parent=Dialog)
        self.desktopShortcut.setChecked(True)
        self.desktopShortcut.setObjectName("desktopShortcut")
        self.horizontalLayout.addWidget(self.desktopShortcut)
        self.startmenuShortcut = QtWidgets.QCheckBox(parent=Dialog)
        self.startmenuShortcut.setChecked(True)
        self.startmenuShortcut.setObjectName("startmenuShortcut")
        self.horizontalLayout.addWidget(self.startmenuShortcut)
        self.matlab = QtWidgets.QCheckBox(parent=Dialog)
        self.matlab.setObjectName("matlab")
        self.horizontalLayout.addWidget(self.matlab)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 3)
        self.output_textedit = QtWidgets.QPlainTextEdit(parent=Dialog)
        self.output_textedit.setReadOnly(True)
        self.output_textedit.setObjectName("output_textedit")
        self.gridLayout.addWidget(self.output_textedit, 3, 0, 1, 3)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.buttonBox.setToolTip(_translate("Dialog", "Compile function requires Python to be installed."))
        self.label.setText(_translate("Dialog", "Atomizer ToolBox Installer"))
        self.label_2.setText(_translate("Dialog", "Installation Path"))
        self.desktopShortcut.setText(_translate("Dialog", "Create Desktop Shortcut"))
        self.startmenuShortcut.setText(_translate("Dialog", "Create Startmenu Shortcut"))
        self.matlab.setText(_translate("Dialog", "Install Matlab Functions (Matlab R2023b required)"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())
