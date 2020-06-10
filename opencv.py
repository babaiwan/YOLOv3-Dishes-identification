## -*- coding: utf-8 -*-
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def sumPrice(label):
    thisprice=0
    if(label=='花卷'):
        thisprice=2
    elif(label=='煎蛋'):
        thisprice=2
    elif(label=='烧鸡'):
        thisprice = 15
    elif (label == '鱼'):
        thisprice = 10
    elif (label == '粽子'):
        thisprice = 5
    return thisprice

def cv2ImgAddText(img, text,left, top):
    img  = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fillColor=(255,0,0)
    fontStyle = ImageFont.truetype("font/simsun.ttc", 20, encoding='utf-8')
    draw.text((left, top-20), text, font=fontStyle ,fill=fillColor)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

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

cap = cv2.VideoCapture(0)

while True:
    # Start timer (for calculating frame rate)
    t1 = cv2.getTickCount()

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
            price = price+sumPrice(label)

    print('total price is '+str(price))
    frame = cv2ImgAddText(frame, '总价为: '+str(price), 15, 20)
 #   cv2.putText(frame,'total Price is '+str(price),(15,15),font,0.7,(255,255,255),1)
    cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc), (30,50),font, 0.7, (255,255,0), 1)
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", 960, 540)
    cv2.imshow("Image", frame)


    # Calculate framerate
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc= 1/time1

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
