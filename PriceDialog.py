# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PriceDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog


class Ui_Dialog(QDialog):
    def setupUi(self, Dialog):
        Dialog.setObjectName("今日菜单")
        Dialog.resize(400, 368)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(290, 130, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 10, 71, 21))
        self.label.setObjectName("label")
        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(50, 90, 141, 221))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.huajuanPrie = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.huajuanPrie.setObjectName("huajuanPrie")
        self.gridLayout.addWidget(self.huajuanPrie, 2, 1, 1, 1)
        self.eagPrice = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.eagPrice.setObjectName("eagPrice")
        self.gridLayout.addWidget(self.eagPrice, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.zongziPrice = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.zongziPrice.setObjectName("zongziPrice")
        self.gridLayout.addWidget(self.zongziPrice, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)
        self.chickenPrice = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.chickenPrice.setObjectName("chickenPrice")
        self.gridLayout.addWidget(self.chickenPrice, 3, 1, 1, 1)
        self.fishPrice = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.fishPrice.setObjectName("fishPrice")
        self.gridLayout.addWidget(self.fishPrice, 4, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(150, 70, 72, 15))
        self.label_7.setObjectName("label_7")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "今日菜单:"))
        self.huajuanPrie.setText(_translate("Dialog", "2"))
        self.eagPrice.setText(_translate("Dialog", "1"))
        self.label_4.setText(_translate("Dialog", "花卷"))
        self.label_3.setText(_translate("Dialog", "粽子"))
        self.label_5.setText(_translate("Dialog", "烧鸡"))
        self.label_2.setText(_translate("Dialog", "煎蛋"))
        self.zongziPrice.setText(_translate("Dialog", "2"))
        self.label_6.setText(_translate("Dialog", "清蒸鱼"))
        self.chickenPrice.setText(_translate("Dialog", "15"))
        self.fishPrice.setText(_translate("Dialog", "10"))
        self.label_7.setText(_translate("Dialog", "单价（元）"))

    def __init__(self):
        super(Ui_Dialog, self).__init__()
        self.setupUi(self)