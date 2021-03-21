'''
Description: -
Version: -
Author: Fox_benjiaming
Date: 2020-11-06 14:05:04
LastEditors: Fox_benjiaming
LastEditTime: 2021-03-21 13:45:53
'''
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QImage

import cv2
import numpy as np

def mat2QImage(cvImg):
    height, width, channels = cvImg.shape
    if channels == 3:
        cvImg = cv2.cvtColor(cvImg, cv2.COLOR_BGR2RGB)
        qImg = QImage(cvImg.tobytes(), width, height,
                      width*channels, QImage.Format_RGB888)
    elif channels == 1:
        qImg = QImage(cvImg.tobytes(), width, height,
                      width*channels, QImage.Format_Indexed8)
    else:
        qImg = QImage(cvImg.tobytes(), width, height,
                      width*channels, QImage.Format_Indexed8)
    return qImg


class ThreadCamera(QThread):
    def __init__(self):
        super().__init__()
        self.img_frame = None
        self.end_flag = False
        self.cap_ip = "192.168.1.88"
        self.cap_rate = "/12"

    def run(self) -> None:
        print("ThreadCamera run!")
        if self.cap_ip:
            try:
                self.cap = cv2.VideoCapture("rtsp://"+self.cap_ip+self.cap_rate)
                while not self.end_flag and self.cap.isOpened():
                    _, frame = self.cap.read()
                    self.img_frame = mat2QImage(frame)
                self.cap.release()
                self.img_frame = None
            except:
                print("Can't open video!")
        print("ThreadFaceDetect finished!")
