# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Python\py_record_psd\ui\record\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(313, 180)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.SaveSizeHeightLineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.SaveSizeHeightLineEdit.setObjectName("SaveSizeHeightLineEdit")
        self.gridLayout.addWidget(self.SaveSizeHeightLineEdit, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 2)
        self.SaveSizeWidthLineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.SaveSizeWidthLineEdit.setObjectName("SaveSizeWidthLineEdit")
        self.gridLayout.addWidget(self.SaveSizeWidthLineEdit, 2, 0, 1, 1)
        self.StopButton = QtWidgets.QPushButton(self.centralWidget)
        self.StopButton.setObjectName("StopButton")
        self.gridLayout.addWidget(self.StopButton, 5, 1, 1, 1)
        self.ShowDirectoryButton = QtWidgets.QPushButton(self.centralWidget)
        self.ShowDirectoryButton.setObjectName("ShowDirectoryButton")
        self.gridLayout.addWidget(self.ShowDirectoryButton, 4, 0, 1, 2)
        self.StartButton = QtWidgets.QPushButton(self.centralWidget)
        self.StartButton.setObjectName("StartButton")
        self.gridLayout.addWidget(self.StartButton, 5, 0, 1, 1)
        self.PSDPathLineInput = QtWidgets.QLineEdit(self.centralWidget)
        self.PSDPathLineInput.setObjectName("PSDPathLineInput")
        self.gridLayout.addWidget(self.PSDPathLineInput, 1, 0, 1, 2)
        self.MakeDivisable16Button = QtWidgets.QPushButton(self.centralWidget)
        self.MakeDivisable16Button.setObjectName("MakeDivisable16Button")
        self.gridLayout.addWidget(self.MakeDivisable16Button, 3, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.SaveSizeHeightLineEdit.setPlaceholderText(_translate("MainWindow", "Height"))
        self.SaveSizeWidthLineEdit.setPlaceholderText(_translate("MainWindow", "WIdth"))
        self.StopButton.setText(_translate("MainWindow", "Stop"))
        self.ShowDirectoryButton.setText(_translate("MainWindow", "Show Directory"))
        self.StartButton.setText(_translate("MainWindow", "Start"))
        self.PSDPathLineInput.setPlaceholderText(_translate("MainWindow", "Active PSD Path"))
        self.MakeDivisable16Button.setText(_translate("MainWindow", "Make PSDoc Divisable by 16"))

