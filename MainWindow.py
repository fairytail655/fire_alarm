'''
Description: -
Version: -
Author: Fox_benjiaming
Date: 2021-03-21 09:44:53
LastEditors: Fox_benjiaming
LastEditTime: 2021-04-03 11:24:47
'''
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtGui import QPixmap, QCloseEvent, QPalette

import socket
import json
import threading
import time

from Ui_MainWindow import Ui_MainWindow
from SerialPort import SerialPort
from MyCombox import MyCombox
from Threads import *
from tcp_logic import TcpServer


TEMP_MIN_VALUE = 0
TEMP_MAX_VALUE = 100
IR_MIN_VALUE = 0
IR_MAX_VALUE = 100
SMOKE_MIN_VALUE = 0
SMOKE_MAX_VALUE = 5
FIRE_MIN_VALUE = 0
FIRE_MAX_VALUE = 5

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
        self.serial_port.readyRead.connect(self.serial_read)

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

        # 报警值配置
        self.device1_temp_alarm = float(self.lineEdit_device1_temp.text())
        self.device1_ir_alarm = float(self.lineEdit_device1_ir.text())
        self.device1_smoke_alarm = float(self.lineEdit_device1_smoke.text())
        self.device1_fire_alarm = float(self.lineEdit_device1_fire.text())
        self.device2_temp_alarm = float(self.lineEdit_device2_temp.text())
        self.device2_ir_alarm = float(self.lineEdit_device2_ir.text())
        self.device2_smoke_alarm = float(self.lineEdit_device2_smoke.text())
        self.device2_fire_alarm = float(self.lineEdit_device2_fire.text())

        # 按钮和报警值关联
        self.pushButton_device_temp.clicked.connect(self.onPushButton_device1_temp)
        self.pushButton_device1_ir.clicked.connect(self.onPushButton_device1_ir)
        self.pushButton_device1_smoke.clicked.connect(self.onPushButton_device1_smoke)
        self.pushButton_device1_fire.clicked.connect(self.onPushButton_device1_fire)
        self.pushButton_device2_temp.clicked.connect(self.onPushButton_device2_temp)
        self.pushButton_device2_ir.clicked.connect(self.onPushButton_device2_ir)
        self.pushButton_device2_smoke.clicked.connect(self.onPushButton_device2_smoke)
        self.pushButton_device2_fire.clicked.connect(self.onPushButton_device2_fire)

        # 设置进度条
        self.progressBar_device1_ir.setMaximum(self.device1_ir_alarm*100)
        self.progressBar_device1_ir.setValue((int)(self.device1_ir_alarm*50))
        self.progressBar_device1_smoke.setMaximum(self.device1_smoke_alarm*100)
        self.progressBar_device1_smoke.setValue((int)(self.device1_smoke_alarm*50))
        self.progressBar_device1_fire1.setMaximum(self.device1_fire_alarm*100)
        self.progressBar_device1_fire1.setValue((int)(self.device1_fire_alarm*50))
        self.progressBar_device1_fire2.setMaximum(self.device1_fire_alarm*100)
        self.progressBar_device1_fire2.setValue((int)(self.device1_fire_alarm*50))
        self.progressBar_device1_fire3.setMaximum(self.device1_fire_alarm*100)
        self.progressBar_device1_fire3.setValue((int)(self.device1_fire_alarm*50))
        self.progressBar_device2_ir.setMaximum(self.device1_ir_alarm*100)
        self.progressBar_device2_ir.setValue((int)(self.device1_ir_alarm*50))
        self.progressBar_device2_smoke.setMaximum(self.device1_smoke_alarm*100)
        self.progressBar_device2_smoke.setValue((int)(self.device1_smoke_alarm*50))
        self.progressBar_device2_fire1.setMaximum(self.device1_fire_alarm*100)
        self.progressBar_device2_fire1.setValue((int)(self.device1_fire_alarm*50))
        self.progressBar_device2_fire2.setMaximum(self.device1_fire_alarm*100)
        self.progressBar_device2_fire2.setValue((int)(self.device1_fire_alarm*50))
        self.progressBar_device2_fire3.setMaximum(self.device1_fire_alarm*100)
        self.progressBar_device2_fire3.setValue((int)(self.device1_fire_alarm*50))
        self.set_progress_value(False)
        self.set_progress_value(True)

        # 摄像头显示进程配置
        self.thread_camera = ThreadCamera()

        # 创建定时器，用于定时读取摄像头进程中的图像
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.slotTimerTimeout)

        # 设备状态初始化
        self.label_device1_online.setVisible(False)
        self.label_device1_offline.setVisible(True)
        self.label_device2_online.setVisible(False)
        self.label_device2_offline.setVisible(True)

        # 创建定时器，用于定时关闭设备状态
        self.timer_2 = QTimer(self)
        self.timer_2.setInterval(5000)
        # self.timer_2.setSingleShot(True)
        self.timer_2.timeout.connect(self.slotTimer_2Timeout)
        self.timer_3 = QTimer(self)
        self.timer_3.setInterval(5000)
        # self.timer_3.setSingleShot(True)
        self.timer_3.timeout.connect(self.slotTimer_3Timeout)

        # 开关按钮配置
        self.pushButton_flag = True
        self.pushButton_switch.clicked.connect(self.onPushButton_ClickedSlot)

        # 自动获取ip
        self.auto_get_ip()
        # 开启tcp server
        self.tcp_server_start()

        # 绑定tcp数据接收信号
        self.sign_tcp_msg.connect(self.slot_tcp_msg)

        # 报警线程
        self.alarm_device1_times = 0
        self.alarm_device2_times = 0
        self.thread_alarm = ThreadAlarm()
        self.thread_alarm.serial_write_signal.connect(self.serial_write)
        self.thread_alarm.save_image_signal.connect(self.thread_camera.save_image)
        self.thread_alarm.finish_signal.connect(self.slot_alarm_finish)

    # 设置进度条右侧的值
    def set_progress_value(self, is_device1):
        if is_device1:
            self.label_device1_ir.setText(str(self.progressBar_device1_ir.value()/100))
            self.label_device1_smoke.setText(str(self.progressBar_device1_smoke.value()/100))
            self.label_device1_fire1.setText(str(self.progressBar_device1_fire1.value()/100))
            self.label_device1_fire2.setText(str(self.progressBar_device1_fire2.value()/100))
            self.label_device1_fire3.setText(str(self.progressBar_device1_fire3.value()/100))
        else:
            self.label_device2_ir.setText(str(self.progressBar_device2_ir.value()/100))
            self.label_device2_smoke.setText(str(self.progressBar_device2_smoke.value()/100))
            self.label_device2_fire1.setText(str(self.progressBar_device2_fire1.value()/100))
            self.label_device2_fire2.setText(str(self.progressBar_device2_fire2.value()/100))
            self.label_device2_fire3.setText(str(self.progressBar_device2_fire3.value()/100))

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

    # 定时器2到达时间
    def slotTimer_2Timeout(self):
        self.label_device1_online.setVisible(False)
        self.label_device1_offline.setVisible(True)
        self.timer_2.stop()

    # 定时器3到达时间
    def slotTimer_3Timeout(self):
        self.label_device2_online.setVisible(False)
        self.label_device2_offline.setVisible(True)
        self.timer_3.stop()

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

    # 接收到TCP Client发送来的数据
    def slot_tcp_msg(self, str):
        self.alarm_device1_times = 0
        self.alarm_device2_times = 0
        # try:
        data_dict = json.loads(str)
        if data_dict['device'] == '1':
            # 设置在线
            self.label_device1_online.setVisible(True)
            self.label_device1_offline.setVisible(False)
            self.timer_2.start()
            # 温度显示
            if float(data_dict['temp']) < self.device1_temp_alarm:
                self.lcdNumber_device1_temp.setStyleSheet('color: green;')
            else:
                self.lcdNumber_device1_temp.setStyleSheet('color: red;')
                self.alarm_device1_times += 1
            self.lcdNumber_device1_temp.display(data_dict['temp'])
            # 热成像显示
            temp = float(data_dict['ir'])
            if temp >= self.device1_ir_alarm:
                self.alarm_device1_times += 1
                self.progressBar_device1_ir.setValue(self.device1_ir_alarm*100)
                self.progressBar_device1_ir.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device1_ir_alarm/2: 
                self.progressBar_device1_ir.setValue((int)(temp*100))
                self.progressBar_device1_ir.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device1_ir.setValue((int)(temp*100))
                self.progressBar_device1_ir.setStyleSheet("QProgressBar::chunk{background:green}")
            # 烟雾显示
            temp = float(data_dict['smoke'])
            if temp >= self.device1_smoke_alarm:
                self.alarm_device1_times += 1
                self.progressBar_device1_smoke.setValue(self.device1_smoke_alarm*100)
                self.progressBar_device1_smoke.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device1_smoke_alarm/2: 
                self.progressBar_device1_smoke.setValue((int)(temp*100))
                self.progressBar_device1_smoke.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device1_smoke.setValue((int)(temp*100))
                self.progressBar_device1_smoke.setStyleSheet("QProgressBar::chunk{background:green}")
            # 火焰显示
            temp = float(data_dict['fire1'])
            if temp >= self.device1_fire_alarm:
                self.alarm_device1_times += 1
                self.progressBar_device1_fire1.setValue(self.device1_fire_alarm*100)
                self.progressBar_device1_fire1.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device1_fire_alarm/2: 
                self.progressBar_device1_fire1.setValue((int)(temp*100))
                self.progressBar_device1_fire1.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device1_fire1.setValue((int)(temp*100))
                self.progressBar_device1_fire1.setStyleSheet("QProgressBar::chunk{background:green}")
            temp = float(data_dict['fire2'])
            if temp >= self.device1_fire_alarm:
                self.alarm_device1_times += 1
                self.progressBar_device1_fire2.setValue(self.device1_fire_alarm*100)
                self.progressBar_device1_fire2.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device1_fire_alarm/2: 
                self.progressBar_device1_fire2.setValue((int)(temp*100))
                self.progressBar_device1_fire2.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device1_fire2.setValue((int)(temp*100))
                self.progressBar_device1_fire2.setStyleSheet("QProgressBar::chunk{background:green}")
            temp = float(data_dict['fire3'])
            if temp >= self.device1_fire_alarm:
                self.alarm_device1_times += 1
                self.progressBar_device1_fire3.setValue(self.device1_fire_alarm*100)
                self.progressBar_device1_fire3.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device1_fire_alarm/2: 
                self.progressBar_device1_fire3.setValue((int)(temp*100))
                self.progressBar_device1_fire3.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device1_fire3.setValue((int)(temp*100))
                self.progressBar_device1_fire3.setStyleSheet("QProgressBar::chunk{background:green}")
            # 更新进度条右侧数值
            self.set_progress_value(True)
        elif data_dict['device'] == '2':
            # 设置在线
            self.label_device2_online.setVisible(True)
            self.label_device2_offline.setVisible(False)
            self.timer_3.start()
            # 温度显示
            if float(data_dict['temp']) < self.device2_temp_alarm:
                self.lcdNumber_device2_temp.setStyleSheet('color: green;')
            else:
                self.alarm_device2_times += 1
                self.lcdNumber_device2_temp.setStyleSheet('color: red;')
            self.lcdNumber_device2_temp.display(data_dict['temp'])
            # 热成像显示
            temp = float(data_dict['ir'])
            if temp >= self.device2_ir_alarm:
                self.alarm_device2_times += 1
                self.progressBar_device2_ir.setValue(self.device2_ir_alarm*100)
                self.progressBar_device2_ir.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device2_ir_alarm/2: 
                self.progressBar_device2_ir.setValue((int)(temp*100))
                self.progressBar_device2_ir.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device2_ir.setValue((int)(temp*100))
                self.progressBar_device2_ir.setStyleSheet("QProgressBar::chunk{background:green}")
            # 烟雾显示
            temp = float(data_dict['smoke'])
            if temp >= self.device2_smoke_alarm:
                self.alarm_device2_times += 1
                self.progressBar_device2_smoke.setValue(self.device2_smoke_alarm*100)
                self.progressBar_device2_smoke.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device2_smoke_alarm/2: 
                self.progressBar_device2_smoke.setValue((int)(temp*100))
                self.progressBar_device2_smoke.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device2_smoke.setValue((int)(temp*100))
                self.progressBar_device2_smoke.setStyleSheet("QProgressBar::chunk{background:green}")
            # 火焰显示
            temp = float(data_dict['fire1'])
            if temp >= self.device2_fire_alarm:
                self.alarm_device2_times += 1
                self.progressBar_device2_fire1.setValue(self.device2_fire_alarm*100)
                self.progressBar_device2_fire1.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device2_fire_alarm/2: 
                self.progressBar_device2_fire1.setValue((int)(temp*100))
                self.progressBar_device2_fire1.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device2_fire1.setValue((int)(temp*100))
                self.progressBar_device2_fire1.setStyleSheet("QProgressBar::chunk{background:green}")
            temp = float(data_dict['fire2'])
            if temp >= self.device2_fire_alarm:
                self.alarm_device2_times += 1
                self.progressBar_device2_fire2.setValue(self.device2_fire_alarm*100)
                self.progressBar_device2_fire2.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device2_fire_alarm/2: 
                self.progressBar_device2_fire2.setValue((int)(temp*100))
                self.progressBar_device2_fire2.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device2_fire2.setValue((int)(temp*100))
                self.progressBar_device2_fire2.setStyleSheet("QProgressBar::chunk{background:green}")
            temp = float(data_dict['fire3'])
            if temp >= self.device2_fire_alarm:
                self.alarm_device2_times += 1
                self.progressBar_device2_fire3.setValue(self.device2_fire_alarm*100)
                self.progressBar_device2_fire3.setStyleSheet("QProgressBar::chunk{background:red}")
            elif temp >= self.device2_fire_alarm/2: 
                self.progressBar_device2_fire3.setValue((int)(temp*100))
                self.progressBar_device2_fire3.setStyleSheet("QProgressBar::chunk{background:yellow}")
            else:
                self.progressBar_device2_fire3.setValue((int)(temp*100))
                self.progressBar_device2_fire3.setStyleSheet("QProgressBar::chunk{background:green}")
            # 更新进度条右侧数值
            self.set_progress_value(False)
        else:
            print("unkown device!")
        # 决定是否报警
        if not self.thread_alarm.isRunning():
            if self.alarm_device1_times > 1:
                self.thread_alarm.is_device1 = True
                self.thread_alarm.phone = self.lineEdit_telephone.text()
                self.thread_alarm.start()
                self.status_label.setText("Device1 detected fire! Calling police...")
            elif self.alarm_device2_times > 1:
                self.thread_alarm.is_device1 = False
                self.thread_alarm.phone = self.lineEdit_telephone.text()
                self.thread_alarm.start()
                self.status_label.setText("Device2 detected fire! Calling police...")
        # except:
        #     print("TCP Client data error")

    def onPushButton_device1_temp(self):
        value = float(self.lineEdit_device1_temp.text())
        if value < TEMP_MIN_VALUE:
            value = TEMP_MIN_VALUE
        elif value > TEMP_MAX_VALUE:
            value = TEMP_MAX_VALUE
        self.device1_temp_alarm = value
        self.lineEdit_device1_temp.setText(str(value))

    def onPushButton_device1_ir(self):
        value = float(self.lineEdit_device1_ir.text())
        if value < IR_MIN_VALUE:
            value = IR_MIN_VALUE
        elif value > IR_MAX_VALUE:
            value = IR_MAX_VALUE
        self.device1_ir_alarm = value
        self.progressBar_device1_ir.setMaximum((int)(value*100))
        self.lineEdit_device1_ir.setText(str(value))

    def onPushButton_device1_smoke(self):
        value = float(self.lineEdit_device1_smoke.text())
        if value < SMOKE_MIN_VALUE:
            value = SMOKE_MIN_VALUE
        elif value > SMOKE_MAX_VALUE:
            value = SMOKE_MAX_VALUE
        self.device1_smoke_alarm = value
        self.progressBar_device1_smoke.setMaximum((int)(value*100))
        self.lineEdit_device1_smoke.setText(str(value))

    def onPushButton_device1_fire(self):
        value = float(self.lineEdit_device1_fire.text())
        if value < FIRE_MIN_VALUE:
            value = FIRE_MIN_VALUE
        elif value > FIRE_MAX_VALUE:
            value = FIRE_MAX_VALUE
        self.device1_fire_alarm = value
        self.progressBar_device1_fire1.setMaximum((int)(value*100))
        self.progressBar_device1_fire2.setMaximum((int)(value*100))
        self.progressBar_device1_fire3.setMaximum((int)(value*100))
        self.lineEdit_device1_fire.setText(str(value))

    def onPushButton_device2_temp(self):
        value = float(self.lineEdit_device2_temp.text())
        if value < TEMP_MIN_VALUE:
            value = TEMP_MIN_VALUE
        elif value > TEMP_MAX_VALUE:
            value = TEMP_MAX_VALUE
        self.device2_temp_alarm = value

    def onPushButton_device2_ir(self):
        value = float(self.lineEdit_device2_ir.text())
        if value < IR_MIN_VALUE:
            value = IR_MIN_VALUE
        elif value > IR_MAX_VALUE:
            value = IR_MAX_VALUE
        self.device2_ir_alarm = value
        self.progressBar_device2_ir.setMaximum((int)(value*100))
        self.lineEdit_device2_ir.setText(str(value))

    def onPushButton_device2_smoke(self):
        value = float(self.lineEdit_device2_smoke.text())
        if value < SMOKE_MIN_VALUE:
            value = SMOKE_MIN_VALUE
        elif value > SMOKE_MAX_VALUE:
            value = SMOKE_MAX_VALUE
        self.device2_smoke_alarm = value
        self.progressBar_device2_smoke.setMaximum((int)(value*100))
        self.lineEdit_device2_smoke.setText(str(value))

    def onPushButton_device2_fire(self):
        value = float(self.lineEdit_device2_fire.text())
        if value < FIRE_MIN_VALUE:
            value = FIRE_MIN_VALUE
        elif value > FIRE_MAX_VALUE:
            value = FIRE_MAX_VALUE
        self.device2_fire_alarm = value
        self.progressBar_device2_fire1.setMaximum((int)(value*100))
        self.progressBar_device2_fire2.setMaximum((int)(value*100))
        self.progressBar_device2_fire3.setMaximum((int)(value*100))
        self.lineEdit_device2_fire.setText(str(value))

    def slot_alarm_finish(self):
        self.status_label.setText("Alarm finished!")

    def serial_write(self, data, data_bytes):
        if data_bytes == b"":
            data_bytes = data.encode(encoding="utf-8")
        self.serial_port.writeData(data_bytes)
        # else:
            # self.serial_port.writeData(self.thread_alarm.data_bytes)

    def serial_read(self):
        data = bytes(self.serial_port.readAll())
        try:
            data_str = data.decode(encoding='utf-8')
            print(data_str)
        except:
            pass
            # print("serial read error")

    # 窗口关闭事件
    def closeEvent(self, event):
        self.tcp_close_flag = True
        self.serial_port.close()
        while self.link:
            pass
        event.accept()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
