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
        MainWindow.resize(283, 430)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.FrameRateLineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.FrameRateLineEdit.setObjectName("FrameRateLineEdit")
        self.gridLayout.addWidget(self.FrameRateLineEdit, 8, 0, 1, 1)
        self.MakeDivisable16Button = QtWidgets.QPushButton(self.centralWidget)
        self.MakeDivisable16Button.setObjectName("MakeDivisable16Button")
        self.gridLayout.addWidget(self.MakeDivisable16Button, 3, 0, 1, 1)
        self.ShowDirectoryButton = QtWidgets.QPushButton(self.centralWidget)
        self.ShowDirectoryButton.setObjectName("ShowDirectoryButton")
        self.gridLayout.addWidget(self.ShowDirectoryButton, 3, 1, 1, 1)
        self.StartButton = QtWidgets.QPushButton(self.centralWidget)
        self.StartButton.setObjectName("StartButton")
        self.gridLayout.addWidget(self.StartButton, 6, 1, 1, 1)
        self.SaveSizeHeightLineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.SaveSizeHeightLineEdit.setObjectName("SaveSizeHeightLineEdit")
        self.gridLayout.addWidget(self.SaveSizeHeightLineEdit, 5, 1, 1, 1)
        self.SaveSizeWidthLineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.SaveSizeWidthLineEdit.setObjectName("SaveSizeWidthLineEdit")
        self.gridLayout.addWidget(self.SaveSizeWidthLineEdit, 5, 0, 1, 1)
        self.StopButton = QtWidgets.QPushButton(self.centralWidget)
        self.StopButton.setObjectName("StopButton")
        self.gridLayout.addWidget(self.StopButton, 8, 1, 1, 1)
        self.PSDPathLineInput = QtWidgets.QLineEdit(self.centralWidget)
        self.PSDPathLineInput.setObjectName("PSDPathLineInput")
        self.gridLayout.addWidget(self.PSDPathLineInput, 1, 0, 1, 2)
        self.PreviewLabel = QtWidgets.QLabel(self.centralWidget)
        self.PreviewLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.PreviewLabel.setObjectName("PreviewLabel")
        self.gridLayout.addWidget(self.PreviewLabel, 0, 0, 1, 2)
        self.FileTypeComboBox = QtWidgets.QComboBox(self.centralWidget)
        self.FileTypeComboBox.setObjectName("FileTypeComboBox")
        self.FileTypeComboBox.addItem("")
        self.FileTypeComboBox.addItem("")
        self.gridLayout.addWidget(self.FileTypeComboBox, 6, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.PSDPathLineInput, self.MakeDivisable16Button)
        MainWindow.setTabOrder(self.MakeDivisable16Button, self.ShowDirectoryButton)
        MainWindow.setTabOrder(self.ShowDirectoryButton, self.SaveSizeWidthLineEdit)
        MainWindow.setTabOrder(self.SaveSizeWidthLineEdit, self.SaveSizeHeightLineEdit)
        MainWindow.setTabOrder(self.SaveSizeHeightLineEdit, self.FileTypeComboBox)
        MainWindow.setTabOrder(self.FileTypeComboBox, self.StartButton)
        MainWindow.setTabOrder(self.StartButton, self.FrameRateLineEdit)
        MainWindow.setTabOrder(self.FrameRateLineEdit, self.StopButton)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.FrameRateLineEdit.setPlaceholderText(_translate("MainWindow", "Framerate"))
        self.MakeDivisable16Button.setText(_translate("MainWindow", "Resize d16"))
        self.ShowDirectoryButton.setText(_translate("MainWindow", "Explore Directory"))
        self.StartButton.setText(_translate("MainWindow", "Start"))
        self.SaveSizeHeightLineEdit.setPlaceholderText(_translate("MainWindow", "Height"))
        self.SaveSizeWidthLineEdit.setPlaceholderText(_translate("MainWindow", "WIdth"))
        self.StopButton.setText(_translate("MainWindow", "Encode GIF/MP4"))
        self.PSDPathLineInput.setPlaceholderText(_translate("MainWindow", "Active PSD Path"))
        self.PreviewLabel.setText(_translate("MainWindow", "[Preview Here]"))
        self.FileTypeComboBox.setItemText(0, _translate("MainWindow", "jpg"))
        self.FileTypeComboBox.setItemText(1, _translate("MainWindow", "png"))

