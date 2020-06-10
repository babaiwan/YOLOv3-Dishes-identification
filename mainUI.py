# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainUI.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!
import os
import sys
import threading
import time
import numpy
import addFont
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import yolo

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QLineEdit
from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtGui import QPalette, QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal, QDateTime, QTimer


def cv2ImgAddText(img, text, left, top):  # 视频帧绘制中文
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fillColor = (255, 0, 0)
    fontStyle = ImageFont.truetype("font/simsun.ttc", 20, encoding='utf-8')
    draw.text((left, top - 20), text, font=fontStyle, fill=fillColor)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
#主窗体
class Ui_MainWindow(object):                                                #主线程
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(90, 110, 111, 81))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(90, 360, 111, 81))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(90, 230, 111, 81))
        self.pushButton_3.setObjectName("pushButton_3")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(110, 90, 72, 15))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(110, 210, 72, 15))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(110, 340, 72, 15))
        self.label_3.setObjectName("label_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

#移除图片按钮
        self.removePicTure = QtWidgets.QPushButton("移除图片",self.centralwidget)
        self.removePicTure.setGeometry(QtCore.QRect(210, 110, 80, 81))
        self.removePicTure.setObjectName("pushButton")
        self.removePicTure.setObjectName("移除图片")
        self.removePicTure.clicked.connect(self.RemovePicture)

#显示图片区域
        self.Photelabel=QLabel("图片",self)
        self.Photelabel.setGeometry(QtCore.QRect(300,120,60,15))
        self.Photelabel.setPixmap(QPixmap("huajuan.jpg"))
        self.Photelabel.resize(640,480)
        self.Photelabel.setScaledContents(True)

#文本框
        # create textbox
        self.input = QLineEdit(self)
        self.input.resize(400,100)



        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "识别图片"))
        self.pushButton_2.setText(_translate("MainWindow", "实时识别"))
        self.pushButton_3.setText(_translate("MainWindow", "识别视频"))

#定义信号  连接到槽函数#
        self.pushButton.clicked.connect(self.ProcessPicture)
        self.pushButton_2.clicked.connect(self.getFrame)
        # self.pushButton_3.clicked.connect(self.ProcessVedio)
        self.pushButton_3.clicked.connect(self.getFrame)             #连接到时间槽函数

#槽函数的定义
    def ProcessPicture(self):
        print("按下了处理图片按钮")
        fd = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
        jpg = QtGui.QPixmap(fd).scaled(self.Photelabel.width(), self.Photelabel.height())       #图片自适应
        self.Photelabel.setPixmap(jpg)
    def ProcessVedio(self):
        print("按下了处理视频按钮")
        fd= QFileDialog.getOpenFileName(self, '选择一个视频文件', './', 'ALL(*.*);;Videos(*.mp4)')
        os.chdir(r'D:\Python\kears-yolov3-dev\kears-yolo-test\keras-yolo3-master')  # 进入指定的目录
        os.system("python yolo_video.py " + fd[0])
    def RemovePicture(self):
        self.cap.release()
        self.Photelabel.setText(" ")
    def getTime(self):                                              #点击按钮，启动获取时间的线程
        self.backend = BackendThread()
        self.backend.update_time.connect(self.updateTimeUI)         #线程绑定更新主线程的UI函数
        self.backend.start()

    def getFrame(self):                                                    #点击按钮，启动实时视频流的线程
        th = threading.Thread(target=self.RealTimeThread)                  #创建视频线程
        th.start()


    def RealTimeThread(self):                                              #实时识别的子线程，不断update视频帧在Qlabel上
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

            self.Photelabel.setPixmap(QPixmap.fromImage(img))
            self.Photelabel.setScaledContents(True)

    def updateTimeUI(self,data):                                    #更新主界面UI  Time函数
        self.input.setText(data)



class BackendThread(QtCore.QThread):                                #新开一个更新时间的子线程
    update_time = pyqtSignal(str)                                   #通过类成员对象定义信号对象
    def run(self):                                                  #线程执行的操作    ->  实时识别
        while True:
            data = QDateTime.currentDateTime()
            currentTime = data.toString("yyyy-MM-dd hh:mm:ss")
            self.update_time.emit(str(currentTime))
            time.sleep(1)

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())