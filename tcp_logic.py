'''
Description: -
Version: -
Author: Fox_benjiaming
Date: 2021-03-21 14:11:49
LastEditors: Fox_benjiaming
LastEditTime: 2021-03-21 16:08:33
'''
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import socket
import threading
import sys
from stopThreading import stop_thread

TCP_SERVER_PORT = 8080

class TcpServer(object):
    sign_tcp_msg = QtCore.pyqtSignal(str)
    def __init__(self):
        self.tcp_socket = None
        self.sever_th = None
        self.link = False  # 用于标记是否开启了连接
        self.client_socket_list = []
        self.tcp_close_flag = False

    def tcp_server_start(self):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 取消主动断开连接四次握手后的TIME_WAIT状态
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 设定套接字为非阻塞式
        self.tcp_socket.setblocking(False)
        port = TCP_SERVER_PORT
        self.tcp_socket.bind(('', port))
        self.tcp_socket.listen()
        self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
        self.sever_th.start()
        msg = 'TCP服务端正在监听端口:%s\n' % str(port)
        print(msg)

    def tcp_server_concurrency(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化
        :return:None
        """
        while True:
            try:
                client_socket, client_address = self.tcp_socket.accept()
            except Exception as ret:
                pass
            else:
                client_socket.setblocking(False)
                # 将创建的客户端套接字存入列表,client_address为ip和端口的元组
                self.client_socket_list.append((client_socket, client_address))
                msg = 'TCP服务端已连接IP:%s端口:%s\n' % client_address
                print(msg)
            # 轮询客户端套接字列表，接收数据
            try:
                for client, address in self.client_socket_list:
                    try:
                        recv_msg = client.recv(1024)
                    except Exception as ret:
                        pass
                    else:
                        if recv_msg:
                            msg = recv_msg.decode('utf-8')
                            self.sign_tcp_msg.emit(msg)
                            msg = '来自IP:{}端口:{}:\n{}\n'.format(address[0], address[1], msg)
                            print(msg)
                        else:
                            client.close()
                            self.client_socket_list.remove((client, address))
            except:
                pass
            # 关闭
            if self.tcp_close_flag:
                self.tcp_close()
                self.link = False
                self.tcp_close_flag = False
                break
            else:
                self.link = True

    def tcp_send(self):
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """
        if self.link is False:
            msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit(msg)
        else:
            try:
                send_msg = (str(self.textEdit_send.toPlainText())).encode('utf-8')
                if self.comboBox_tcp.currentIndex() == 0:
                    # 向所有连接的客户端发送消息
                    for client, address in self.client_socket_list:
                        client.send(send_msg)
                    msg = 'TCP服务端已发送\n'
                    self.signal_write_msg.emit(msg)
                if self.comboBox_tcp.currentIndex() == 1:
                    self.tcp_socket.send(send_msg)
                    msg = 'TCP客户端已发送\n'
                    self.signal_write_msg.emit(msg)
            except Exception as ret:
                msg = '发送失败\n'
                self.signal_write_msg.emit(msg)

    def tcp_close(self):
        """
        功能函数，关闭网络连接的方法
        :return:
        """
        try:
            for client, address in self.client_socket_list:
                client.close()
            self.tcp_socket.close()
        except Exception as ret:
            pass