# coding=utf-8
# cv2解决绘制中文乱码
 
import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont

class Font():
    def cv2ImgAddText(img, text, left, top):  # 视频帧绘制中文
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        fillColor = (255, 0, 0)
        fontStyle = ImageFont.truetype("font/simsun.ttc", 20, encoding='utf-8')
        draw.text((left, top - 20), text, font=fontStyle, fill=fillColor)
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
