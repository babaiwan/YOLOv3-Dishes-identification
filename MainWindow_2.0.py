# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow_2.0.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!
import os
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageQt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QDateTime
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from PriceDialog import Ui_Dialog
from yolo import YOLO

def cv2ImgAddText(img, text, left, top):  # 视频帧中绘制中文
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)      #通过打开一个Img，生成一个draw对象。
    fillColor = (255, 0, 0)         #设置图片颜色
    fontStyle = ImageFont.truetype("font/simsun.ttc", 20, encoding='utf-8')     #其中字体需要自行去下载，将字体放在font目录下
    draw.text((left, top - 20), text, font=fontStyle, fill=fillColor)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)   #这个函数在视频帧中处理，不断调用


def sumPrice(label):
    thisprice = 0
    if (label == '花卷'):
        thisprice = 2
    elif (label == '煎蛋'):
        thisprice = 1
    elif (label == '烧鸡'):
        thisprice = 15
    elif (label == '鱼'):
        thisprice = 10
    elif (label == '粽子'):
        thisprice = 2
    return thisprice

class UpdatePrice(QtCore.QThread):                                  #新开一个更新图像和价格的子线程
    update_price = pyqtSignal(str)                                  #通过类成员对象定义信号对象
    update_variety = pyqtSignal(str)                                #更新菜品种类和数目的信号
    update_picture = pyqtSignal(QImage)

    def __init__(self):
        super(UpdatePrice, self).__init__()
        self.flag = 1                                               # 用来判断循环是否继续的标志，通过改变该标志来使得线程中run函数退出

    def run(self):                                                  #线程执行的操作    ->  实时识别
        print("启动实时识别的线程")
        # Load Yolo
        net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
        classes = []
        with open("coco.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))

        # Initialize frame rate calculation
        frame_rate_calc = 1
        freq = cv2.getTickFrequency()
        cap = cv2.VideoCapture(0)  # 打开摄像头
        print("实时识别的线程加载完毕")

        while True:
            print("正在识别")
            ret, frame = cap.read()
            height, width, channels = frame.shape

            # Detecting objects
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

            net.setInput(blob)
            outs = net.forward(output_layers)

            # Showing informations on the screen
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.4:
                        # Object detected
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)

                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            price = 0
            meal=''
            font = cv2.FONT_HERSHEY_SIMPLEX

            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = colors[i]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1)
                    frame = cv2ImgAddText(frame, label, x, y)
                    price = price + sumPrice(label)
                    meal=meal+label+'\n'
                    self.update_variety.emit(meal)
            # print('total price is ' + str(price))
            frame = cv2ImgAddText(frame, '总价为: ' + str(price), 15, 20)

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            img = QImage(frame.data, width, height, QImage.Format_RGB888)


            self.update_picture.emit(img)                                                   #传递信号
            self.update_price.emit("总价为: "+str(price))

class BackendThread(QtCore.QThread):                                #新开一个更新时间的子线程
    update_time = pyqtSignal(str)                                   #通过类成员对象定义信号对象
    def run(self):                                                  #线程执行的操作    ->  实时识别
        print("启动 显示当前时间 的线程")
        while True:
            data = QDateTime.currentDateTime()
            currentTime = data.toString("hh:mm:ss")
            self.update_time.emit(str(currentTime))
            time.sleep(1)


class Ui_MainWindow(object):
    print("加载网络模型")
    yolo = YOLO()
    print("实例化Yolo完成")

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.PhotoLabel = QtWidgets.QLabel(self.centralwidget)
        self.PhotoLabel.setGeometry(QtCore.QRect(50, 40, 441, 411))
        self.PhotoLabel.setStyleSheet("background-color: rgb(142, 144, 147);")
        self.PhotoLabel.setText("")
        self.PhotoLabel.setObjectName("PhotoLabel")
        self.PriceZone = QtWidgets.QLineEdit(self.centralwidget)
        self.PriceZone.setGeometry(QtCore.QRect(590, 310, 141, 41))
        self.PriceZone.setObjectName("PriceZone")
        self.TimeZone = QtWidgets.QLineEdit(self.centralwidget)
        self.TimeZone.setGeometry(QtCore.QRect(130, 0, 141, 31))
        self.TimeZone.setObjectName("TimeZone")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(50, 10, 72, 15))
        self.label_3.setObjectName("label_3")
        self.showTimeButton = QtWidgets.QPushButton(self.centralwidget)
        self.showTimeButton.setGeometry(QtCore.QRect(280, 0, 71, 31))
        self.showTimeButton.setObjectName("showTimeButton")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(530, 70, 201, 161))
        self.frame.setStyleSheet("background-color: rgb(194, 194, 194);\n"
"border-color: rgb(12, 2, 34);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.frame)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 9, 181, 141))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ProcessPicture = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.ProcessPicture.setStyleSheet("\n"
"background-color: rgb(243, 255, 249);")
        self.ProcessPicture.setObjectName("ProcessPicture")
        self.verticalLayout.addWidget(self.ProcessPicture)
        self.RealTimeButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.RealTimeButton.setStyleSheet("\n"
"background-color: rgb(243, 255, 249);")
        self.RealTimeButton.setObjectName("RealTimeButton")
        self.verticalLayout.addWidget(self.RealTimeButton)
        self.ClearQlabel = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.ClearQlabel.setStyleSheet("\n"
"background-color: rgb(243, 255, 249);")
        self.ClearQlabel.setObjectName("ClearQlabel")
        self.verticalLayout.addWidget(self.ClearQlabel)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(530, 50, 101, 16))
        self.label_2.setStyleSheet("")
        self.label_2.setObjectName("label_2")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(520, 290, 221, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(510, 50, 20, 191))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(730, 50, 20, 191))
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(520, 40, 221, 16))
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setGeometry(QtCore.QRect(520, 480, 221, 16))
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.line_6 = QtWidgets.QFrame(self.centralwidget)
        self.line_6.setGeometry(QtCore.QRect(730, 300, 20, 181))
        self.line_6.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.line_7 = QtWidgets.QFrame(self.centralwidget)
        self.line_7.setGeometry(QtCore.QRect(510, 300, 20, 181))
        self.line_7.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.line_8 = QtWidgets.QFrame(self.centralwidget)
        self.line_8.setGeometry(QtCore.QRect(520, 240, 221, 16))
        self.line_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(50, 470, 101, 16))
        self.label_5.setStyleSheet("")
        self.label_5.setObjectName("label_5")
        self.PriceZone_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.PriceZone_2.setGeometry(QtCore.QRect(530, 360, 201, 121))
        self.PriceZone_2.setObjectName("PriceZone_2")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(110, 460, 381, 81))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.CutScreenButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.CutScreenButton.setObjectName("CutScreenButton")
        self.horizontalLayout.addWidget(self.CutScreenButton)
        self.CutScreenButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.CutScreenButton_2.setObjectName("CutScreenButton_2")
        self.horizontalLayout.addWidget(self.CutScreenButton_2)
        self.ExitButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.ExitButton.setObjectName("ExitButton")
        self.horizontalLayout.addWidget(self.ExitButton)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(530, 320, 101, 16))
        self.label_4.setStyleSheet("")
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_3.setText(_translate("MainWindow", "当前时间:"))
        self.showTimeButton.setText(_translate("MainWindow", "显示时间"))
        self.ProcessPicture.setText(_translate("MainWindow", "识别图像"))
        self.RealTimeButton.setText(_translate("MainWindow", "实时识别"))
        self.ClearQlabel.setText(_translate("MainWindow", "清除屏幕"))
        self.label_2.setText(_translate("MainWindow", "识别区:"))
        self.label_5.setText(_translate("MainWindow", "功能区:"))
        self.CutScreenButton.setText(_translate("MainWindow", "截屏"))
        self.CutScreenButton_2.setText(_translate("MainWindow", "今日菜单"))
        self.ExitButton.setText(_translate("MainWindow", "退出"))
        self.label_4.setText(_translate("MainWindow", "计价区："))

# 连接信号槽
        self.showTimeButton.clicked.connect(self.updateTime)
        self.RealTimeButton.clicked.connect(self.updateFrame)
        self.CutScreenButton.clicked.connect(self.cutscreen)
        self.ProcessPicture.clicked.connect(self.showPicture)
        self.ExitButton.clicked.connect(self.close)
        self.ClearQlabel.clicked.connect(self.clearQlabel)
        self.CutScreenButton_2.clicked.connect(self.showMenu)

# 获取当前时间相关函数
    def updateTime(self):  # 点击按钮，启动获取时间的线程
        self.backend = BackendThread()
        self.backend.update_time.connect(self.updateTimeUI)  # 线程绑定更新主线程的UI函数
        self.backend.start()
    def updateTimeUI(self, data):  # 更新主界面UI  Time函数
        self.TimeZone.setText(data)

#图片识别相关函数
    def showPicture(self):
        # path, _ = QFileDialog.getOpenFileName(self, '选择图片', 'D:\Python\kears-yolov3-dev\OpenCVtest',
        #                                       'Image files(*.jpg *.gif *.png)')
        # img = Image.open(path)
        # r_image = self.yolo.detect_image(img)  # r_image 为  PIL    图片数据格式


        image = Image.open('D:\Python\kears-yolov3-dev\OpenCVtest\huajuan1111.jpg')
        r_image = self.yolo.detect_image(image)


        qim = ImageQt(r_image)  # PIL   ->     Pixmap    格式转换
        pix = QtGui.QPixmap.fromImage(qim)


        self.PhotoLabel.setPixmap(pix)                  # 图像更新到UI上
        self.PhotoLabel.setScaledContents(True)

#清除Qlabel函数
    def clearQlabel(self):
        print("清除屏幕")
        pix = QPixmap(" ")
        self.PhotoLabel.setPixmap(pix)

# 计价显示模块相关函数
    def updateFrame(self):  # 点击按钮，启动实时视频流的线程
        self.updatePrice = UpdatePrice()
        self.updatePrice.update_price.connect(self.updatePriceUI)      # 线程绑定更新主线程的UI函数
        self.updatePrice.update_variety.connect(self.updateVareity)    # 线程绑定更新主线程的UI函数
        self.updatePrice.update_picture.connect(self.updatePictureUI)  # 线程绑定更新主线程的UI函数
        self.updatePrice.start()
    def updatePriceUI(self, data):   # 更新主界面UI  价格
        self.PriceZone.setText(data)
    def updateVareity(self,data):    # 更新主界面UI  显示菜品数目和种类

        self.PriceZone_2.setText(data)

    def updatePictureUI(self, img):  # 更新主界面UI  图像      接受QImage格式
        self.PhotoLabel.setPixmap(QPixmap.fromImage(img))  # 图像更新到UI上
        self.PhotoLabel.setScaledContents(True)            # 设置图像大小自适应
#控件截图函数
    def cutscreen(self):
        print("截图Qlabel")
        screen = QApplication.primaryScreen()
        pix = screen.grabWindow(self.PhotoLabel.winId())
        t = time.time()
        pix.save(str(t)+".jpg")
#关闭事件
    def close(self):
        # 关闭事件设为触发，关闭视频播放
        os.system("pkill python")
#显示菜单相关函数:
    def showMenu(self):
        PirceDialog.show()

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    PirceDialog = Ui_Dialog()
    myWin.show()
    sys.exit(app.exec_())
