'''
Description: -
Version: -
Author: Fox_benjiaming
Date: 2021-03-21 09:44:53
LastEditors: Fox_benjiaming
LastEditTime: 2021-03-21 15:26:19
'''
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtGui import QPixmap

import socket

from Ui_MainWindow import Ui_MainWindow
from SerialPort import SerialPort
from MyCombox import MyCombox
from Threads import ThreadCamera
from tcp_logic import TcpServer


class MainWindow(QMainWindow, Ui_MainWindow, TcpServer):
    def __init__(self):
        super(MainWindow, self).__init__()
        TcpServer.__init__(self)
        self.setupUi(self)

        # 状态栏配置
        self.status_label = QtWidgets.QLabel()
        self.status_label.setText("Hello word!")
        self.statusbar.addWidget(self.status_label)

        # 串口配置
        self.comboBox = MyCombox(self.centralwidget)
        x = 670 + 97
        y = 20 + 10
        self.comboBox.setGeometry(QtCore.QRect(x, y, 115, 33))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setMinimumSize(QtCore.QSize(0, 30))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.enter_event_signal.connect(self.onCombox_EnterSlot)
        self.serial_port = SerialPort()
        self.serial_port.searchPort()
        self.serial_list =  list(self.serial_port.port.keys())
        self.serial_list.sort()
        for item in self.serial_list:
            self.comboBox.addItem(item)
        self.comboBox_baudrate.addItem('1200')
        self.comboBox_baudrate.addItem('2400')
        self.comboBox_baudrate.addItem('4800')
        self.comboBox_baudrate.addItem('9600')
        self.comboBox_baudrate.addItem('19200')
        self.comboBox_baudrate.addItem('38400')
        self.comboBox_baudrate.addItem('57600')
        self.comboBox_baudrate.addItem('115200')
        self.comboBox_baudrate.setCurrentIndex(7)
        self.serial_port.baund_rate = QSerialPort.Baud115200
        self.comboBox_baudrate.currentIndexChanged.connect(self.onCombox_baudrate_IncdeChangeSlot)
        self.comboBox_stopBit.addItem('1')
        self.comboBox_stopBit.addItem('1.5')
        self.comboBox_stopBit.addItem('2')
        self.comboBox_stopBit.setCurrentIndex(0)
        self.comboBox_stopBit.currentIndexChanged.connect(self.onCombox_stopBit_IncdeChangeSlot)
        self.comboBox_dataBit.addItem('5')
        self.comboBox_dataBit.addItem('6')
        self.comboBox_dataBit.addItem('7')
        self.comboBox_dataBit.addItem('8')
        self.comboBox_dataBit.setCurrentIndex(3)
        self.comboBox_dataBit.currentIndexChanged.connect(self.onCombox_dataBit_IncdeChangeSlot)
        self.comboBox_parity.addItem('无')
        self.comboBox_parity.addItem('奇校验')
        self.comboBox_parity.addItem('偶校验')
        self.comboBox_parity.setCurrentIndex(0)
        self.comboBox_parity.currentIndexChanged.connect(self.onCombox_parity_IncdeChangeSlot)

        # 摄像头显示进程配置
        self.thread_camera = ThreadCamera()

        # 创建定时器，用于定时读取摄像头进程中的图像
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.slotTimerTimeout)

        # 开关按钮配置
        self.pushButton_flag = True
        self.pushButton_switch.clicked.connect(self.onPushButton_ClickedSlot)

        # 自动获取ip
        self.auto_get_ip()
        self.tcp_server_start()

    # 获取本机ip
    def auto_get_ip(self):
        self.lineEdit_ip.clear()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        my_addr = s.getsockname()[0]
        self.lineEdit_ip.setText(str(my_addr))
        s.close()

    # 串口号选择
    def onCombox_EnterSlot(self):
        if self.pushButton_flag:
            index = self.comboBox.currentIndex()
            text = self.comboBox.currentText()
            self.comboBox.clear()
            self.serial_port.searchPort()
            self.serial_list = list(self.serial_port.port.keys())
            self.serial_list.sort()
            for item in self.serial_list:
                self.comboBox.addItem(item)
            self.comboBox.setCurrentIndex(index)
            if self.comboBox.currentText() != text:
                self.comboBox.setCurrentIndex(0)

    # 串口波特率选择
    def onCombox_baudrate_IncdeChangeSlot(self):
        current_index = self.comboBox_baudrate.currentIndex()
        if current_index == 0:
            self.serial_port.baund_rate = QSerialPort.Baud1200
        elif current_index == 1:
            self.serial_port.baund_rate = QSerialPort.Baud2400
        elif current_index == 2:
            self.serial_port.baund_rate = QSerialPort.Baud4800
        elif current_index == 3:
            self.serial_port.baund_rate = QSerialPort.Baud9600
        elif current_index == 4:
            self.serial_port.baund_rate = QSerialPort.Baud19200
        elif current_index == 5:
            self.serial_port.baund_rate = QSerialPort.Baud38400
        elif current_index == 6:
            self.serial_port.baund_rate = QSerialPort.Baud57600
        elif current_index == 7:
            self.serial_port.baund_rate = QSerialPort.Baud115200

    # 串口停止位选择
    def onCombox_stopBit_IncdeChangeSlot(self):
        current_index = self.comboBox_stopBit.currentIndex()
        if current_index == 0:
            self.serial_port.stop_bits = QSerialPort.OneStop
        elif current_index == 1:
            self.serial_port.stop_bits = QSerialPort.OneAndHalfStop
        elif current_index == 2:
            self.serial_port.stop_bits = QSerialPort.TwoStop

    # 串口数据位选择
    def onCombox_dataBit_IncdeChangeSlot(self):
        current_index = self.comboBox_dataBit.currentIndex()
        if current_index == 0:
            self.serial_port.data_bits = QSerialPort.Data5
        elif current_index == 1:
            self.serial_port.data_bits = QSerialPort.Data6
        elif current_index == 2:
            self.serial_port.data_bits = QSerialPort.Data7
        elif current_index == 3:
            self.serial_port.data_bits = QSerialPort.Data8

    # 串口奇偶校验位选择
    def onCombox_parity_IncdeChangeSlot(self):
        current_index = self.comboBox_parity.currentIndex()
        if current_index == 0:
            self.serial_port.parity = QSerialPort.NoParity
        elif current_index == 1:
            self.serial_port.parity = QSerialPort.OddParity
        elif current_index == 2:
            self.serial_port.parity = QSerialPort.EvenParity

    # 定时器到达时间间隔的槽函数
    def slotTimerTimeout(self):
        if self.thread_camera.img_frame and (not self.thread_camera.end_flag):
            self.label_video.setPixmap(QPixmap.fromImage(self.thread_camera.img_frame))
        else:
            self.label_video.clear()

    # 按钮按下动作
    def onPushButton_ClickedSlot(self):
        if self.pushButton_flag:
            port_name = self.comboBox.currentText()
            if port_name != '':
                self.serial_port.setPort(self.serial_port.port[port_name])
                self.serial_port.open(QSerialPort.ReadWrite)
                self.serial_port.setBaudRate(self.serial_port.baund_rate)
                self.serial_port.setStopBits(self.serial_port.stop_bits)
                self.serial_port.setDataBits(self.serial_port.data_bits)
                self.serial_port.setParity(self.serial_port.parity)

                self.pushButton_flag = False
                self.pushButton_switch.setStyleSheet("border-image: url(:/on/on.png);")
                self.comboBox.setEnabled(False)
                self.comboBox_baudrate.setEnabled(False)
                self.comboBox_stopBit.setEnabled(False)
                self.comboBox_dataBit.setEnabled(False)
                self.comboBox_parity.setEnabled(False)

                self.thread_camera.end_flag = False
                self.thread_camera.start()
                self.timer.start()

                self.lineEdit_ip.setReadOnly(True)
                self.lineEdit_telephone.setReadOnly(True)
            else:
                QMessageBox.warning(None, "Warning!", "Cannot detect serial!")
        else:
            self.serial_port.close()
            self.pushButton_flag = True
            self.pushButton_switch.setStyleSheet("border-image: url(:/off/off.png);")
            self.comboBox.setEnabled(True)
            self.comboBox_baudrate.setEnabled(True)
            self.comboBox_stopBit.setEnabled(True)
            self.comboBox_dataBit.setEnabled(True)
            self.comboBox_parity.setEnabled(True)

            self.timer.stop()
            self.thread_camera.end_flag = True
            self.label_video.clear()

            self.lineEdit_ip.setReadOnly(False)
            self.lineEdit_telephone.setReadOnly(False)

    def closeEvent():

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
