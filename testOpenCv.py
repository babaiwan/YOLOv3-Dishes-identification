import cv2    #引入cv2，也就是引入opencv的一些包和处理类，不然下面的一些操作都无法完成

#打开摄像头的方法，window_name为显示窗口名，video_id为你设备摄像头的id，默认为0或-1，如果引用usb可能会改变为1，等
def openvideo(window_name ,video_id):
    cv2.namedWindow(window_name) # 创建一个窗口

    cap=cv2.VideoCapture(video_id) # 获取摄像头
    while cap.isOpened():
        ok,frame=cap.read() # ok表示摄像头读取状态，frame表示摄像头读取的图像
        if not ok :
            break

        cv2.imshow(window_name,frame) # 将图像矩阵显示在一个窗口中
        c=cv2.waitKey(1000) # 等待10ms，10ms内没有按键操作就进入下一次while循环，从而得到10ms一帧的效果，waitKey返回在键盘上按的键
        if c & 0xFF==ord('q'): # 按键q后break
            break

    # 释放资源
    cap.release()
    cv2.destroyWindow(window_name)
    print("cam closed")

# 主程序调用方法运行
if __name__ == '__main__': # __name__ 是当前模块名，当模块被直接运行时模块名为 __main__ 。这句话的意思就是，当模块被直接运行时，以下代码块将被运行，当模块是被导入时，代码块不被运行。
    print ('open camera...')
    openvideo('mycam' ,0)