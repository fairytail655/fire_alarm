from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice

class SerialPort(QSerialPort):
    def __init__(self):
        """
        初始化串口变量
        """
        super().__init__()
        self.port = {}
        self.baund_rate = QSerialPort.Baud9600
        self.data_bits = QSerialPort.Data8
        self.parity = QSerialPort.NoParity
        self.stop_bits = QSerialPort.OneStop

    def searchPort(self):
        """
        搜索可用的串口，并存储起来：{串口名：串口信息}
        """
        info_list = QSerialPortInfo.availablePorts()
        self.port = {}
        for info in info_list:
            serial = QSerialPort()
            serial.setPort(info)
            if serial.open(QIODevice.ReadWrite):
                self.port[serial.portName()] = info
                serial.close()
