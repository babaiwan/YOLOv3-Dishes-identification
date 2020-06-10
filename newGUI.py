# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newGUI.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!
import sys
import threading
import time

import cv2
import numpy
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageQt import ImageQt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QDateTime
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from yolo import YOLO


def cv2ImgAddText(img, text, left, top):  # 视频帧绘制中文
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fillColor = (255, 0, 0)
    fontStyle = ImageFont.truetype("font/simsun.ttc", 20, encoding='utf-8')
    draw.text((left, top - 20), text, font=fontStyle, fill=fillColor)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.priceText = QtWidgets.QTextEdit(self.centralwidget)
        self.priceText.setGeometry(QtCore.QRect(340, 390, 231, 111))
        self.priceText.setObjectName("priceText")
        self.Photelabel = QtWidgets.QLabel(self.centralwidget)
        self.Photelabel.setGeometry(QtCore.QRect(340, 70, 381, 291))
        self.Photelabel.setStyleSheet("background-color: rgb(244, 247, 255);")
        self.Photelabel.setText("")
        self.Photelabel.setObjectName("ShowPicArea")
        self.stopLabel = QtWidgets.QPushButton(self.centralwidget)
        self.stopLabel.setGeometry(QtCore.QRect(610, 390, 111, 111))
        self.stopLabel.setObjectName("stopLabel")
        self.pictureButton = QtWidgets.QPushButton(self.centralwidget)
        self.pictureButton.setGeometry(QtCore.QRect(100, 140, 141, 61))
        self.pictureButton.setObjectName("pictureButton")
        self.realTimeButton = QtWidgets.QPushButton(self.centralwidget)
        self.realTimeButton.setGeometry(QtCore.QRect(100, 230, 141, 61))
        self.realTimeButton.setObjectName("realTimeButton")
        self.getTime = QtWidgets.QPushButton(self.centralwidget)
        self.getTime.setGeometry(QtCore.QRect(570, 10, 51, 31))
        self.getTime.setObjectName("getTime")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(630, 10, 151, 33))
        self.textEdit.setObjectName("textEdit")
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
        self.stopLabel.setText(_translate("MainWindow", "Stop"))
        self.pictureButton.setText(_translate("MainWindow", "识别图片"))
        self.realTimeButton.setText(_translate("MainWindow", "实时识别"))
        self.getTime.setText(_translate("MainWindow", "Time"))

#按钮连接的函数
        self.getTime.clicked.connect(self.updateTime)
        self.realTimeButton.clicked.connect(self.updateFrame)
        self.pictureButton.clicked.connect(self.showPicture)

        self.stopLabel.clicked.connect(self.cutscreen)

    def showPicture(self):
        print("加载网络模型")
        yolo = YOLO()
        print("实例化Yolo完成，打开图片--")
        path, _ = QFileDialog.getOpenFileName(self, '选择图片', 'D:\Python\kears-yolov3-dev\OpenCVtest', 'Image files(*.jpg *.gif *.png)')

        img=Image.open(path)
        r_image = yolo.detect_image(img)                            # r_image 为  PIL    图片数据格式

        qim = ImageQt(r_image)                                      # PIL   ->     Pixmap    格式转换
        pix = QtGui.QPixmap.fromImage(qim)

        self.Photelabel.setPixmap(pix)                              # 图像更新到UI上
        self.Photelabel.setScaledContents(True)

#时间控件相关函数
    def updateTime(self):                                           # 点击按钮，启动获取时间的线程
        self.backend = BackendThread()
        self.backend.update_time.connect(self.updateTimeUI)         # 线程绑定更新主线程的UI函数
        self.backend.start()
    def updateTimeUI(self,data):                                    # 更新主界面UI  Time函数
        self.textEdit.setText(data)

#实时识别相关函数
    def updateFrame(self):                                                 #点击按钮，启动实时视频流的线程
        # th = threading.Thread(target=self.RealTimeThread)  # 创建视频线程
        # th.start()
        self.updatePrice = UpdatePrice()
        self.updatePrice.update_price.connect(self.updatePriceUI)          #线程绑定更新主线程的UI函数
        self.updatePrice.update_picture.connect(self.updatePictureUI)      #线程绑定更新主线程的UI函数

        self.updatePrice.start()

    def updatePriceUI(self,data):                                    # 更新主界面UI  价格
        self.priceText.setText(data)
    def updatePictureUI(self,img):                                   # 更新主界面UI  图像      接受QImage格式
        self.Photelabel.setPixmap(QPixmap.fromImage(img))            # 图像更新到UI上
        self.Photelabel.setScaledContents(True)

    def RealTimeThread(self):  # 实时识别的子线程，不断update视频帧在Qlabel上
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

        ##############################################回传实时识别信号##########################################################
        while True:
            # # Start timer (for calculating frame rate)
            # t1 = cv2.getTickCount()

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
            font = cv2.FONT_HERSHEY_SIMPLEX
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = colors[i]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1)
                    frame = cv2ImgAddText(frame, label, x, y)
                #    price = price + sumPrice(label)

            print('total price is ' + str(price))
            frame = cv2ImgAddText(frame, '总价为: ' + str(price), 15, 20)

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            img = QImage(frame.data, width, height, QImage.Format_RGB888)

            self.Photelabel.setPixmap(QPixmap.fromImage(img))  # 图像更新到UI上
            self.Photelabel.setScaledContents(True)
#控件截图函数
    def cutscreen(self):
        print("截图Qlabel")
        screen = QApplication.primaryScreen()
        pix = screen.grabWindow(self.Photelabel.winId())
        pix.save("test.jpg")


def sumPrice(label):
    thisprice = 0
    if (label == '花卷'):
        thisprice = 2
    elif (label == '煎蛋'):
        thisprice = 2
    elif (label == '烧鸡'):
        thisprice = 15
    elif (label == '鱼'):
        thisprice = 10
    elif (label == '粽子'):
        thisprice = 5
    return thisprice

class UpdatePrice(QtCore.QThread):                                  #新开一个更新图像和价格的子线程
    update_price = pyqtSignal(str)                                  #通过类成员对象定义信号对象
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
            font = cv2.FONT_HERSHEY_SIMPLEX
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = colors[i]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1)
                    frame = cv2ImgAddText(frame, label, x, y)
                    price = price + sumPrice(label)

            print('total price is ' + str(price))
            frame = cv2ImgAddText(frame, '总价为: ' + str(price), 15, 20)

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            img = QImage(frame.data, width, height, QImage.Format_RGB888)


            self.update_picture.emit(img)                                                   #传递信号
            self.update_price.emit("总价为: "+str(price))


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)

class BackendThread(QtCore.QThread):                                #新开一个更新时间的子线程
    update_time = pyqtSignal(str)                                   #通过类成员对象定义信号对象
    def run(self):                                                  #线程执行的操作    ->  实时识别
        print("启动 显示当前时间 的线程")
        while True:
            data = QDateTime.currentDateTime()
            currentTime = data.toString("hh:mm:ss")
            self.update_time.emit(str(currentTime))
            time.sleep(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())