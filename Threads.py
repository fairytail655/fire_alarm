'''
Description: -
Version: -
Author: Fox_benjiaming
Date: 2020-11-06 14:05:04
LastEditors: Fox_benjiaming
LastEditTime: 2021-04-03 10:37:14
'''
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5.QtGui import QImage

import cv2
import numpy as np

from time import sleep

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
        self.img = None
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
                    self.img = frame
                    self.img_frame = mat2QImage(frame)
                self.cap.release()
                self.img_frame = None
            except:
                print("Can't open video!")
        print("ThreadFaceDetect finished!")

    def save_image(self):
        img = cv2.resize(self.img, (320, 176))
        cv2.imwrite('fire.png', img)


class ThreadAlarm(QThread):
    serial_write_signal = pyqtSignal(str, bytes)
    save_image_signal = pyqtSignal()
    finish_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.is_device1 = None
        self.phone = None

    def run(self) -> None:
        print("ThreadAlarm run!")
        self.save_image_signal.emit()
        # 打电话
        self.serial_write_signal.emit("AT+CTTSPARAM=20,0,50,50,1\r\n", b"")
        sleep(0.2)
        self.serial_write_signal.emit("ATD" + self.phone + ";\r\n", b"")
        sleep(10)
        if self.is_device1:
            self.serial_write_signal.emit("AT+CTTS=1,\"60A8597D00208FD991CC662F67D05C0F533A57304E0B8F665E937684706B707E62A58B667CFB7EDF0020003153F78F664F4D53D1751F706B707E00208BF75C3D5FEB524D6765706D706B\"\r\n", b"")
        else:
            self.serial_write_signal.emit("AT+CTTS=1,\"60A8597D00208FD991CC662F67D05C0F533A57304E0B8F665E937684706B707E62A58B667CFB7EDF0020003253F78F664F4D53D1751F706B707E00208BF75C3D5FEB524D6765706D706B\"\r\n", b"")
        sleep(15)
        self.serial_write_signal.emit("ATH\r\n", b"")
        sleep(1)
        # 发彩信
        self.serial_write_signal.emit("AT+CMMSINIT\r\n", b"")
        sleep(1)
        self.serial_write_signal.emit("AT+CMMSCURL=\"mmsc.monternet.com\"\r\n", b"")
        sleep(1)
        self.serial_write_signal.emit("AT+CMMSCID=1\r\n", b"")
        sleep(1)
        self.serial_write_signal.emit("AT+CMMSPROTO=\"10.0.0.172\",80\r\n", b"")
        sleep(1)
        self.serial_write_signal.emit("AT+CMMSSENDCFG=6,3,0,0,2,4\r\n", b"")
        sleep(1)
        self.serial_write_signal.emit("AT+SAPBR=3,1,\"Contype\",\"GPRS\"\r\n", b"")
        sleep(2)
        self.serial_write_signal.emit("AT+SAPBR=3,1,\"APN\",\"CMWAP\"\r\n", b"")
        sleep(2)
        self.serial_write_signal.emit("AT+SAPBR=1,1\r\n", b"")
        sleep(2)
        self.serial_write_signal.emit("AT+SAPBR=2,1\r\n", b"")
        sleep(2)
        self.serial_write_signal.emit("AT+CMMSEDIT=1\r\n", b"")
        sleep(2)
        with open("fire.png","rb") as f:
            data_bytes = f.read()
            self.serial_write_signal.emit("AT+CMMSDOWN=\"PIC\"," + str(len(data_bytes)) + ",80000\r\n", b"")
            sleep(2)
            self.serial_write_signal.emit("a", data_bytes)
        sleep(15)
        self.serial_write_signal.emit("AT+CMMSRECP=\"" + self.phone + "\"\r\n", b"")
        sleep(2)
        self.serial_write_signal.emit("AT+CMMSSEND\r\n", b"")
        sleep(30)
        sleep(30)
        sleep(30)
        sleep(30)
        self.serial_write_signal.emit("AT+CMMSEDIT=0\r\n", b"")
        sleep(1)
        self.serial_write_signal.emit("AT+SAPBR=0,1\r\n", b"")
        sleep(1)
        self.serial_write_signal.emit("AT+CMMSTERM\r\n", b"")
        print("ThreadAlarm finished!")
        self.finish_signal.emit()
