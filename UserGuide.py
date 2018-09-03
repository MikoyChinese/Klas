# -*- coding: utf-8 -*-
"""
author = hobin;
email = '627227669@qq.com';
Api Class: UserGuide(cfg_path='Config.cfg')
"""
import configparser
import sys

import cv2
import numpy
from PyQt5.QtCore import Qt, QIODevice
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QDialog, QHBoxLayout, QVBoxLayout, \
    QPushButton, QLabel, QComboBox, QTextEdit, QMessageBox
from CameraThread import MyCameraThread1_2


class UserGuide01(QDialog):

    def __init__(self, parent=None):
        super(UserGuide01, self).__init__(parent)
        self.width = 600
        self.height = 600
        self.x = 700
        self.y = 300
        # these functions come from QWidget;
        self.move(self.x, self.y)
        self.setFixedSize(self.width, self.height)
        # self.setStyleSheet('background-color: rgb(64,64,64);')
        # self.setWindowFlags()
        self.setWindowTitle('User Guide')


        # layout management
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self.camera_tab1UI()
        self.camera_tab2UI()
        self.weigher_tabUI()

        # cameras
        QCamera()  # You have to declare QCamera object before using QCameraInfo.availableCameras()
        self.camera_list = []
        for index, cam in enumerate(QCameraInfo.availableCameras()):
            self.camera_list.append(cv2.VideoCapture(index))
        # print(self.camera_list)  # [<VideoCapture 000001A465A546D0>, <VideoCapture 000001A465A54790>]
        # print(QCameraInfo.availableCameras())  # [<PyQt5.QtMultimedia.QCameraInfo object at 0x000001A465A1DBA8>, <PyQt5.QtMultimedia.QCameraInfo object at 0x000001A465A1DC88>]

        # threads
        self.thread01 = MyCameraThread1_2(camera_object=None)  # The index of camera should be given carefully.
        self.thread01.update.connect(self.refresh_label01)
        # self.thread01.start()  # It is not safe to start since the camera object might not exist.
        self.thread02 = MyCameraThread1_2(camera_object=None)  # The index of camera should be given carefully.
        self.thread02.update.connect(self.refresh_label02)
        # self.thread02.start()

        # serial port
        self.serialPort_list = QSerialPortInfo.availablePorts()
        for port in self.serialPort_list:
            # print(port.portName())
            self.cbox03.addItem(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setBaudRate(9600)
        self.serial.setDataBits(QSerialPort.DataBits(8))
        self.serial.setStopBits(QSerialPort.StopBits(1))
        self.serial.readyRead.connect(self.serial_acceptData03)

        # the default work
        if len(self.camera_list) > 0:
            self.thread01.capture = self.camera_list[0]
            self.thread01.start()
            self.thread02.capture = self.camera_list[0]
            self.thread02.start()
            for index, item in enumerate(self.camera_list):
                self.cbox01.addItem('Camera%s' %index)
                self.cbox02.addItem('Camera%s' %index)
        else:
            self.label01.setText("No camera found! Please check for the camera and then click the 'refresh' button")
            self.label02.setText("No camera found! Please check for the camera and then click the 'refresh' button")


    def camera_tab1UI(self):
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, 'Camera for Item')
        self.tab_widget.setTabText(0, 'Camera for Item')
        self.main_layout01 = QVBoxLayout()
        self.tab1.setLayout(self.main_layout01)
        self.firstlayout01 = QHBoxLayout()
        self.main_layout01.addLayout(self.firstlayout01)
        self.secondlayout01 = QHBoxLayout()
        self.secondlayout01.setAlignment(Qt.AlignCenter)
        self.main_layout01.addLayout(self.secondlayout01)
        # first layout
        self.label01 = QLabel()
        self.label01.setScaledContents(True)
        self.firstlayout01.addWidget(self.label01)
        self.firstlayout01_right = QVBoxLayout()
        self.firstlayout01.addLayout(self.firstlayout01_right)
        self.cbox01 = QComboBox()
        self.cbox01.currentIndexChanged.connect(self.comboBox_changed01)
        self.firstlayout01_right.addWidget(self.cbox01)
        self.button01_refresh = QPushButton('refresh')
        self.button01_refresh.clicked.connect(self.device_refresh01)
        self.firstlayout01_right.addWidget(self.button01_refresh)
        # second layout
        # self.button01_backward = QPushButton('backward')
        # self.secondlayout01.addWidget(self.button01_backward)
        self.button01_forward = QPushButton('forward')
        self.button01_forward.clicked.connect(self.forward01)
        self.secondlayout01.addWidget(self.button01_forward)


    def comboBox_changed01(self, current_index):
        """
        What if the camera does not exist anymore? The question is how can I detect that.
        By testing, cv2.VideoCapture.isOpened() function cannot tell you whether the camera is exists.
        :param current_index:
        :return:
        """
        if len(QCameraInfo.availableCameras()) == len(self.camera_list):
            self.thread01.capture = self.camera_list[current_index]
            if not self.thread01.isRunning():
                self.thread01.start()
        else:
            print('The camera with index %s is closed (comboBox_changed01).' % current_index)
            self.device_refresh01()


    def refresh_label01(self, img):
        self.label01.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage


    def device_refresh01(self):
        self.thread01.status = False
        self.thread02.status = False
        for cam in self.camera_list:
            cam.release()
        #
        self.camera_list = []
        for index, cam in enumerate(QCameraInfo.availableCameras()):
            self.camera_list.append(cv2.VideoCapture(index))

        if len(self.camera_list) > 0:
            self.thread01.capture = self.camera_list[0]
            self.thread01.start()
            self.thread02.capture = self.camera_list[0]
            self.thread02.start()
            self.cbox01.clear()
            self.cbox02.clear()
            for index, item in enumerate(self.camera_list):
                self.cbox01.addItem('Camera%s' % index)
                self.cbox02.addItem('Camera%s' % index)
            self.tab_widget.setCurrentIndex(0)
        else:
            self.label01.setText("No camera found! Please check for the camera and then click the 'refresh' button")
            self.label02.setText("No camera found! Please check for the camera and then click the 'refresh' button")


    def forward01(self):
        self.tab_widget.setCurrentIndex(1)


    def camera_tab2UI(self):
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, 'Camera for User')
        self.tab_widget.setTabText(1, 'Camera for User')
        self.main_layout02 = QVBoxLayout()
        self.tab2.setLayout(self.main_layout02)
        self.firstlayout02 = QHBoxLayout()
        self.main_layout02.addLayout(self.firstlayout02)
        self.secondlayout02 = QHBoxLayout()
        self.secondlayout02.setAlignment(Qt.AlignCenter)
        self.main_layout02.addLayout(self.secondlayout02)
        # first layout
        self.label02 = QLabel()
        self.label02.setScaledContents(True)
        self.firstlayout02.addWidget(self.label02)
        self.firstlayout02_right = QVBoxLayout()
        self.firstlayout02.addLayout(self.firstlayout02_right)
        self.cbox02 = QComboBox()
        self.cbox02.currentIndexChanged.connect(self.comboBox_changed02)
        self.firstlayout02_right.addWidget(self.cbox02)
        self.button02_refresh = QPushButton('refresh')
        self.button02_refresh.clicked.connect(self.device_refresh01)
        self.firstlayout02_right.addWidget(self.button02_refresh)
        # second layout
        self.button02_backward = QPushButton('backward')
        self.button02_backward.clicked.connect(self.backward02)
        self.secondlayout02.addWidget(self.button02_backward)
        self.button02_forward = QPushButton('forward')
        self.button02_forward.clicked.connect(self.forward02)
        self.secondlayout02.addWidget(self.button02_forward)


    def comboBox_changed02(self, current_index):
        if len(QCameraInfo.availableCameras()) == len(self.camera_list):
            self.thread02.capture = self.camera_list[current_index]
            if not self.thread02.isRunning():
                self.thread02.start()
        else:
            print('The camera with index %s is closed (comboBox_changed02).' % current_index)
            self.device_refresh01()


    def refresh_label02(self, img):
        self.label02.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage


    def forward02(self):
        self.tab_widget.setCurrentIndex(2)


    def backward02(self):
        self.tab_widget.setCurrentIndex(0)


    def weigher_tabUI(self):
        self.tab3 = QWidget()
        self.tab_widget.addTab(self.tab3, 'Weigher')
        self.tab_widget.setTabText(2, 'Weigher')
        self.main_layout03 = QVBoxLayout()
        self.tab3.setLayout(self.main_layout03)
        self.firstlayout03 = QHBoxLayout()
        self.main_layout03.addLayout(self.firstlayout03)
        self.secondlayout03 = QHBoxLayout()
        self.secondlayout03.setAlignment(Qt.AlignCenter)
        self.main_layout03.addLayout(self.secondlayout03)
        # first layout, left layout
        self.firstlayout03_left = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_left)
        self.textedit03 = QTextEdit()
        self.firstlayout03_left.addWidget(self.textedit03)
        self.firstlayout03_right = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_right)
        # first layout , right layout
        self.firstlayout03_right = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_right)
        self.cbox03 = QComboBox()
        self.firstlayout03_right.addWidget(self.cbox03)
        self.button03_open = QPushButton('open')
        self.button03_open.clicked.connect(self.serial_open03)
        self.firstlayout03_right.addWidget(self.button03_open)
        self.button03_close = QPushButton('close')
        self.button03_close.setEnabled(False)
        self.button03_close.clicked.connect(self.serial_close03)
        self.firstlayout03_right.addWidget(self.button03_close)
        self.button03_clear = QPushButton('clear text')
        self.button03_clear.clicked.connect(self.clear_textedit03)
        self.firstlayout03_right.addWidget(self.button03_clear)
        self.button03_refresh = QPushButton('refresh')
        self.button03_refresh.clicked.connect(self.device_refresh03)
        self.firstlayout03_right.addWidget(self.button03_refresh)
        # second layout
        self.button03_backward = QPushButton('backward')
        self.button03_backward.clicked.connect(self.backward03)
        self.secondlayout03.addWidget(self.button03_backward)
        self.button03_forward = QPushButton('confirm')
        self.button03_forward.clicked.connect(self.forward03)
        self.secondlayout03.addWidget(self.button03_forward)


    def serial_open03(self):
        self.serial.setPortName(self.cbox03.currentText())  # passing name such as 'COM1'
        if self.serial.open(QIODevice.ReadOnly):
            # self.serial.setDataTerminalReady(True)  # setting the specific pin to the high-value voltage;
            # print('The reconnection to the serial port is successful.')
            self.button03_open.setEnabled(False)
            self.button03_close.setEnabled(True)
        else:
            reply = QMessageBox.warning(self, 'Warning', 'The reconnection to the serial port is failed.', QMessageBox.Ok)


    def serial_acceptData03(self):
        data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
        data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
        # print('The length of data is %s and the value part is %s' %(len(data2), data2))
        self.textedit03.insertPlainText(data2)


    def serial_close03(self):
        self.serial.close()
        self.button03_open.setEnabled(True)
        self.button03_close.setEnabled(False)


    def clear_textedit03(self):
        self.textedit03.clear()


    def device_refresh03(self):
        self.serialPort_list = []
        self.cbox03.clear()
        self.serialPort_list = QSerialPortInfo.availablePorts()
        for port in self.serialPort_list:
            # print(port.portName())
            self.cbox03.addItem(port.portName())


    def forward03(self):
        """
        Currently, this will get the information from those comboBox and record them into the new cfg file.
        :return:
        """
        message = """
        the number of the item camera: %s
        the number of the user camera: %s
        the number of the serial port: %s
        """ %(self.cbox01.currentIndex(), self.cbox02.currentIndex(), self.cbox03.currentText())
        reply = QMessageBox.question(self, 'Save your selection',message, QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            print('yes')
        else:
            # If user click on the X button, the reply also is the QMessageBox.No;
            # print('no')
            pass


    def backward03(self):
        self.tab_widget.setCurrentIndex(1)


    def closeEvent(self, event):
        self.thread01.status = False
        self.thread02.status = False
        for cam in self.camera_list:
            cam.release()
        self.camera_list = []
        self.serial.close()
        super(UserGuide01, self).closeEvent(event)


class UserGuide02(QDialog):
    """
    Compared with the UserGuide01 class, the main difference is that it will read the original cfg file;
    Another difference is that it saves the configuration into another cfg file (closeEvent);
    Finding one potential bug: QTabWidget.addItem will emit the currentIndexChanged signal.
    The reason might be the default current index is none and the QTabWidget.addItem() cause the current index to 0?
    Another situation is the device_refresh01() also might cause the potential bug.
    """
    def __init__(self, cfg_path='Brindley2.cfg', parent=None):
        super(UserGuide02, self).__init__(parent)
        self.width = 600
        self.height = 600
        self.x = 700
        self.y = 300
        # these functions come from QWidget;
        self.move(self.x, self.y)
        self.setFixedSize(self.width, self.height)
        # self.setStyleSheet('background-color: rgb(64,64,64);')
        # self.setWindowFlags()
        self.setWindowTitle('User Guide')

        # layout management
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self.camera_tab1UI()
        self.camera_tab2UI()
        self.weigher_tabUI()

        # config
        self.cf = configparser.ConfigParser()
        self.cf.read(cfg_path)
        # print(self.cf.sections())

        # cameras
        camera_device = QCamera()  # You have to declare QCamera object before using QCameraInfo.availableCameras()
        self.camera_list = []
        for index, cam in enumerate(QCameraInfo.availableCameras()):
            self.camera_list.append(cv2.VideoCapture(index))
        # print(self.camera_list)  # [<VideoCapture 000001A465A546D0>, <VideoCapture 000001A465A54790>]
        # print(QCameraInfo.availableCameras())  # [<PyQt5.QtMultimedia.QCameraInfo object at 0x000001A465A1DBA8>, <PyQt5.QtMultimedia.QCameraInfo object at 0x000001A465A1DC88>]

        # threads
        self.thread01 = MyCameraThread1_2(camera_object=None)  # The index of camera should be given carefully.
        self.thread01.update.connect(self.refresh_label01)
        # self.thread01.start()  # It is not safe to start since the camera object might not exist.
        self.thread02 = MyCameraThread1_2(camera_object=None)  # The index of camera should be given carefully.
        self.thread02.update.connect(self.refresh_label02)
        # self.thread02.start()

        # serial port
        self.serialPort_list = QSerialPortInfo.availablePorts()
        for port in self.serialPort_list:
            # print(port.portName())
            self.cbox03.addItem(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setBaudRate(9600)
        self.serial.setDataBits(QSerialPort.DataBits(8))
        self.serial.setStopBits(QSerialPort.StopBits(1))
        self.serial.readyRead.connect(self.serial_acceptData03)

        # the default work
        if len(self.camera_list) > 0:
            self.thread01.capture = self.camera_list[0]
            self.thread01.start()
            self.thread02.capture = self.camera_list[0]
            self.thread02.start()
            for index, item in enumerate(self.camera_list):
                self.cbox01.addItem('Camera%s' %index)
                self.cbox02.addItem('Camera%s' %index)
        else:
            self.label01.setText("No camera found! Please check for the camera and then click the 'refresh' button")
            self.label02.setText("No camera found! Please check for the camera and then click the 'refresh' button")

        self.cbox02.currentIndexChanged.connect(self.comboBox_changed02)
        self.cbox01.currentIndexChanged.connect(self.comboBox_changed01)


    def camera_tab1UI(self):
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, 'Camera for Item')
        self.tab_widget.setTabText(0, 'Camera for Item')
        self.main_layout01 = QVBoxLayout()
        self.tab1.setLayout(self.main_layout01)
        self.firstlayout01 = QHBoxLayout()
        self.main_layout01.addLayout(self.firstlayout01)
        self.secondlayout01 = QHBoxLayout()
        self.secondlayout01.setAlignment(Qt.AlignCenter)
        self.main_layout01.addLayout(self.secondlayout01)
        # first layout
        self.label01 = QLabel()
        self.label01.setScaledContents(True)
        self.firstlayout01.addWidget(self.label01)
        self.firstlayout01_right = QVBoxLayout()
        self.firstlayout01.addLayout(self.firstlayout01_right)
        self.cbox01 = QComboBox()
        self.firstlayout01_right.addWidget(self.cbox01)
        self.button01_refresh = QPushButton('refresh')
        self.button01_refresh.clicked.connect(self.device_refresh01)
        self.firstlayout01_right.addWidget(self.button01_refresh)
        # second layout
        # self.button01_backward = QPushButton('backward')
        # self.secondlayout01.addWidget(self.button01_backward)
        self.button01_forward = QPushButton('forward')
        self.button01_forward.clicked.connect(self.forward01)
        self.secondlayout01.addWidget(self.button01_forward)


    def comboBox_changed01(self, current_index):
        """
        What if the camera does not exist anymore? The question is how can I detect that.
        By testing, cv2.VideoCapture.isOpened() function cannot tell you whether the camera is exists.
        :param current_index:
        :return:
        """
        if len(QCameraInfo.availableCameras()) == len(self.camera_list):
            self.thread01.capture = self.camera_list[current_index]
            if not self.thread01.isRunning():
                self.thread01.start()
        else:
            print('The camera with index %s is closed (comboBox_changed01).' % current_index)
            self.device_refresh01()


    def refresh_label01(self, img):
        self.label01.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage


    def device_refresh01(self):
        self.thread01.status = False
        self.thread02.status = False
        for cam in self.camera_list:
            cam.release()
        #
        self.camera_list = []
        for index, cam in enumerate(QCameraInfo.availableCameras()):
            self.camera_list.append(cv2.VideoCapture(index))

        if len(self.camera_list) > 0:
            self.thread01.capture = self.camera_list[0]
            self.thread01.start()
            self.thread02.capture = self.camera_list[0]
            self.thread02.start()
            self.cbox01.clear()
            self.cbox02.clear()
            for index, item in enumerate(self.camera_list):
                self.cbox01.addItem('Camera%s' % index)
                self.cbox02.addItem('Camera%s' % index)
            self.tab_widget.setCurrentIndex(0)
        else:
            self.label01.setText("No camera found! Please check for the camera and then click the 'refresh' button")
            self.label02.setText("No camera found! Please check for the camera and then click the 'refresh' button")


    def forward01(self):
        self.tab_widget.setCurrentIndex(1)


    def camera_tab2UI(self):
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, 'Camera for User')
        self.tab_widget.setTabText(1, 'Camera for User')
        self.main_layout02 = QVBoxLayout()
        self.tab2.setLayout(self.main_layout02)
        self.firstlayout02 = QHBoxLayout()
        self.main_layout02.addLayout(self.firstlayout02)
        self.secondlayout02 = QHBoxLayout()
        self.secondlayout02.setAlignment(Qt.AlignCenter)
        self.main_layout02.addLayout(self.secondlayout02)
        # first layout
        self.label02 = QLabel()
        self.label02.setScaledContents(True)
        self.firstlayout02.addWidget(self.label02)
        self.firstlayout02_right = QVBoxLayout()
        self.firstlayout02.addLayout(self.firstlayout02_right)
        self.cbox02 = QComboBox()
        self.firstlayout02_right.addWidget(self.cbox02)
        self.button02_refresh = QPushButton('refresh')
        self.button02_refresh.clicked.connect(self.device_refresh01)
        self.firstlayout02_right.addWidget(self.button02_refresh)
        # second layout
        self.button02_backward = QPushButton('backward')
        self.button02_backward.clicked.connect(self.backward02)
        self.secondlayout02.addWidget(self.button02_backward)
        self.button02_forward = QPushButton('forward')
        self.button02_forward.clicked.connect(self.forward02)
        self.secondlayout02.addWidget(self.button02_forward)


    def comboBox_changed02(self, current_index):
        if len(QCameraInfo.availableCameras()) == len(self.camera_list):
            self.thread02.capture = self.camera_list[current_index]
            if not self.thread02.isRunning():
                self.thread02.start()
        else:
            print('The camera with index %s is closed (comboBox_changed02).' % current_index)
            self.device_refresh01()


    def refresh_label02(self, img):
        self.label02.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage


    def forward02(self):
        self.tab_widget.setCurrentIndex(2)


    def backward02(self):
        self.tab_widget.setCurrentIndex(0)


    def weigher_tabUI(self):
        self.tab3 = QWidget()
        self.tab_widget.addTab(self.tab3, 'Weigher')
        self.tab_widget.setTabText(2, 'Weigher')
        self.main_layout03 = QVBoxLayout()
        self.tab3.setLayout(self.main_layout03)
        self.firstlayout03 = QHBoxLayout()
        self.main_layout03.addLayout(self.firstlayout03)
        self.secondlayout03 = QHBoxLayout()
        self.secondlayout03.setAlignment(Qt.AlignCenter)
        self.main_layout03.addLayout(self.secondlayout03)
        # first layout, left layout
        self.firstlayout03_left = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_left)
        self.textedit03 = QTextEdit()
        self.firstlayout03_left.addWidget(self.textedit03)
        self.firstlayout03_right = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_right)
        # first layout , right layout
        self.firstlayout03_right = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_right)
        self.cbox03 = QComboBox()
        self.firstlayout03_right.addWidget(self.cbox03)
        self.button03_open = QPushButton('open')
        self.button03_open.clicked.connect(self.serial_open03)
        self.firstlayout03_right.addWidget(self.button03_open)
        self.button03_close = QPushButton('close')
        self.button03_close.setEnabled(False)
        self.button03_close.clicked.connect(self.serial_close03)
        self.firstlayout03_right.addWidget(self.button03_close)
        self.button03_clear = QPushButton('clear text')
        self.button03_clear.clicked.connect(self.clear_textedit03)
        self.firstlayout03_right.addWidget(self.button03_clear)
        self.button03_refresh = QPushButton('refresh')
        self.button03_refresh.clicked.connect(self.device_refresh03)
        self.firstlayout03_right.addWidget(self.button03_refresh)
        # second layout
        self.button03_backward = QPushButton('backward')
        self.button03_backward.clicked.connect(self.backward03)
        self.secondlayout03.addWidget(self.button03_backward)
        self.button03_forward = QPushButton('confirm')
        self.button03_forward.clicked.connect(self.forward03)
        self.secondlayout03.addWidget(self.button03_forward)


    def serial_open03(self):
        self.serial.setPortName(self.cbox03.currentText())  # passing name such as 'COM1'
        if self.serial.open(QIODevice.ReadOnly):
            # self.serial.setDataTerminalReady(True)  # setting the specific pin to the high-value voltage;
            # print('The reconnection to the serial port is successful.')
            self.button03_open.setEnabled(False)
            self.button03_close.setEnabled(True)
        else:
            reply = QMessageBox.warning(self, 'Warning', 'The reconnection to the serial port is failed.', QMessageBox.Ok)


    def serial_acceptData03(self):
        data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
        data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
        # print('The length of data is %s and the value part is %s' %(len(data2), data2))
        self.textedit03.insertPlainText(data2)


    def serial_close03(self):
        self.serial.close()
        self.button03_open.setEnabled(True)
        self.button03_close.setEnabled(False)


    def clear_textedit03(self):
        self.textedit03.clear()


    def device_refresh03(self):
        self.serialPort_list = []
        self.cbox03.clear()
        self.serialPort_list = QSerialPortInfo.availablePorts()
        for port in self.serialPort_list:
            # print(port.portName())
            self.cbox03.addItem(port.portName())


    def forward03(self):
        """
        Currently, this will get the information from those comboBox and record them into the new cfg file.
        :return:
        """
        message = """
        the number of the item camera: %s
        the number of the user camera: %s
        the number of the serial port: %s
        """ %(self.cbox01.currentIndex(), self.cbox02.currentIndex(), self.cbox03.currentText())
        reply = QMessageBox.question(self, 'Save your selection',message, QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # self.cf.set('cam_item','cam_num',str(self.cbox01.currentIndex()))
            # self.cf.set('cam_user','cam_num',str(self.cbox02.currentIndex()))
            # self.cf.set('weigher','port_name',self.cbox03.currentText())
            self.cf['cam_item']['cam_num'] = str(self.cbox01.currentIndex())
            self.cf['cam_user']['cam_num'] = str(self.cbox02.currentIndex())
            self.cf['weigher']['port_name'] = self.cbox03.currentText()
            self.close()
        else:
            # If user click on the X button, the reply also is the QMessageBox.No;
            # print('no')
            pass


    def backward03(self):
        self.tab_widget.setCurrentIndex(1)


    def closeEvent(self, event):
        self.thread01.status = False
        self.thread02.status = False
        for cam in self.camera_list:
            cam.release()
        self.camera_list = []
        self.serial.close()
        with open('Brindley2_auto.cfg', 'w') as configfile:
            self.cf.write(configfile)
        super(UserGuide02, self).closeEvent(event)


class UserGuide03(QDialog):
    """
    Compared with the UserGuide01 class, the main difference is that it will read the original cfg file;
    Another difference is that it saves the configuration into another cfg file (closeEvent);
    Compared with the UserGuide02 class, the UserGuide02_1 class uses self.thread_list rather than self.camera_list;
    Compared with the UserGuide02 class, the UserGuide02_1 class uses signal connection and disconnection to display different frame!
    Compared with the UserGuide02 class, the UserGuide02_1 class uses readAll() at the end of the serial_acceptData03 function.
    """
    def __init__(self, cfg_path='Klas2.cfg', parent=None):
        super(UserGuide03, self).__init__(parent)
        self.cfg_path = cfg_path
        self.width = 600
        self.height = 600
        self.x = 700
        self.y = 300
        # these functions come from QWidget;
        self.move(self.x, self.y)
        self.setFixedSize(self.width, self.height)
        # self.setStyleSheet('background-color: rgb(64,64,64);')
        # self.setWindowFlags()
        self.setWindowTitle('User Guide')

        # layout management
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self.camera_tab1UI()
        self.camera_tab2UI()
        self.weigher_tabUI()

        # config
        self.cf = configparser.ConfigParser()
        self.cf.read(cfg_path)
        # print(self.cf.sections())

        # cameras
        camera_device = QCamera()  # You have to declare QCamera object before using QCameraInfo.availableCameras()
        self.thread_list = []
        for index, cam in enumerate(QCameraInfo.availableCameras()):
            a = MyCameraThread1_2(cv2.VideoCapture(index))
            self.thread_list.append(a)
            a.start()


        # serial port
        self.serialPort_list = QSerialPortInfo.availablePorts()
        for port in self.serialPort_list:
            # print(port.portName())
            self.cbox03.addItem(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setBaudRate(9600)
        self.serial.setDataBits(QSerialPort.DataBits(8))
        self.serial.setStopBits(QSerialPort.StopBits(1))
        self.serial.readyRead.connect(self.serial_acceptData03)

        # the default work
        self.last_index01 = 0
        self.last_index02 = 0
        if len(self.thread_list) > 0:
            self.thread_list[0].update.connect(self.refresh_label01)
            self.thread_list[0].update.connect(self.refresh_label02)
            for index, item in enumerate(self.thread_list):
                self.cbox01.insertItem(index, '%s' %index)
                self.cbox02.insertItem(index, '%s' %index)
        else:
            self.label01.setText("No camera found! Please check for the camera and then click the 'refresh' button")
            self.label02.setText("No camera found! Please check for the camera and then click the 'refresh' button")

        self.cbox02.currentIndexChanged.connect(self.comboBox_changed02)
        self.cbox01.currentIndexChanged.connect(self.comboBox_changed01)

    def camera_tab1UI(self):
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, 'Camera for Item')
        self.tab_widget.setTabText(0, 'Camera for Item')
        self.main_layout01 = QVBoxLayout()
        self.tab1.setLayout(self.main_layout01)
        self.firstlayout01 = QHBoxLayout()
        self.main_layout01.addLayout(self.firstlayout01)
        self.secondlayout01 = QHBoxLayout()
        self.secondlayout01.setAlignment(Qt.AlignCenter)
        self.main_layout01.addLayout(self.secondlayout01)
        # first layout
        self.label01 = QLabel()
        self.label01.setScaledContents(True)
        self.firstlayout01.addWidget(self.label01)
        self.firstlayout01_right = QVBoxLayout()
        self.firstlayout01.addLayout(self.firstlayout01_right)
        self.cbox01 = QComboBox()
        self.firstlayout01_right.addWidget(self.cbox01)
        self.button01_refresh = QPushButton('refresh')
        self.button01_refresh.clicked.connect(self.device_refresh01)
        self.firstlayout01_right.addWidget(self.button01_refresh)
        # second layout
        # self.button01_backward = QPushButton('backward')
        # self.secondlayout01.addWidget(self.button01_backward)
        self.button01_forward = QPushButton('forward')
        self.button01_forward.clicked.connect(self.forward01)
        self.secondlayout01.addWidget(self.button01_forward)


    def comboBox_changed01(self, current_index):
        """
        What if the camera does not exist anymore? The question is how can I detect that.
        By testing, cv2.VideoCapture.isOpened() function cannot tell you whether the camera is exists.
        :param current_index:
        :return:
        """
        print('comboBox_changed01 begins')
        if len(QCameraInfo.availableCameras()) == len(self.thread_list):
            self.thread_list[self.last_index01].update.disconnect(self.refresh_label01)
            self.thread_list[current_index].update.connect(self.refresh_label01)
            self.last_index01 = current_index
            print('comboBox_changed01 ends')
        else:
            print('The camera with index %s is closed (comboBox_changed01 end).' % current_index)
            self.device_refresh01()


    def refresh_label01(self, img):
        # print('refresh_label01 begins')
        if type(img) == QImage:
            self.label01.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage
        # print('refresh_label01 ends')


    def device_refresh01(self):
        print('device_refresh01 begins')
        self.cbox02.currentIndexChanged.disconnect(self.comboBox_changed02)
        self.cbox01.currentIndexChanged.disconnect(self.comboBox_changed01)
        for thread in self.thread_list:
            thread.status = False
            thread.capture.release()
        self.thread_list = []
        for index, cam in enumerate(QCameraInfo.availableCameras()):
            a = MyCameraThread1_2(cv2.VideoCapture(index))
            self.thread_list.append(a)
            a.start()
        self.cbox01.clear()
        self.cbox02.clear()

        self.last_index01 = 0
        self.last_index02 = 0
        if len(self.thread_list) > 0:
            self.thread_list[0].update.connect(self.refresh_label01)
            self.thread_list[0].update.connect(self.refresh_label02)
            for index, item in enumerate(self.thread_list):
                self.cbox01.insertItem(index, '%s' %index)
                self.cbox02.insertItem(index, '%s' %index)
        else:
            self.label01.setText("No camera found! Please check for the camera and then click the 'refresh' button")
            self.label02.setText("No camera found! Please check for the camera and then click the 'refresh' button")
        self.cbox02.currentIndexChanged.connect(self.comboBox_changed02)
        self.cbox01.currentIndexChanged.connect(self.comboBox_changed01)
        print('device_refresh01 ends')


    def forward01(self):
        self.tab_widget.setCurrentIndex(1)


    def camera_tab2UI(self):
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, 'Camera for User')
        self.tab_widget.setTabText(1, 'Camera for User')
        self.main_layout02 = QVBoxLayout()
        self.tab2.setLayout(self.main_layout02)
        self.firstlayout02 = QHBoxLayout()
        self.main_layout02.addLayout(self.firstlayout02)
        self.secondlayout02 = QHBoxLayout()
        self.secondlayout02.setAlignment(Qt.AlignCenter)
        self.main_layout02.addLayout(self.secondlayout02)
        # first layout
        self.label02 = QLabel()
        self.label02.setScaledContents(True)
        self.firstlayout02.addWidget(self.label02)
        self.firstlayout02_right = QVBoxLayout()
        self.firstlayout02.addLayout(self.firstlayout02_right)
        self.cbox02 = QComboBox()

        self.firstlayout02_right.addWidget(self.cbox02)
        self.button02_refresh = QPushButton('refresh')
        self.button02_refresh.clicked.connect(self.device_refresh01)
        self.firstlayout02_right.addWidget(self.button02_refresh)
        # second layout
        self.button02_backward = QPushButton('backward')
        self.button02_backward.clicked.connect(self.backward02)
        self.secondlayout02.addWidget(self.button02_backward)
        self.button02_forward = QPushButton('forward')
        self.button02_forward.clicked.connect(self.forward02)
        self.secondlayout02.addWidget(self.button02_forward)


    def comboBox_changed02(self, current_index):
        print('comboBox_changed02 begins')
        if len(QCameraInfo.availableCameras()) == len(self.thread_list):
            self.thread_list[self.last_index02].update.disconnect(self.refresh_label02)
            self.thread_list[current_index].update.connect(self.refresh_label02)
            self.last_index02 = current_index
            print('comboBox_changed02 ends')
        else:
            print('The camera with index %s is closed (comboBox_changed02 end).' % current_index)
            self.device_refresh01()


    def refresh_label02(self, img):
        # print('refresh_label02 begins')
        if type(img) == QImage:
            self.label02.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage
        # print('refresh_label02 ends')


    def forward02(self):
        self.tab_widget.setCurrentIndex(2)


    def backward02(self):
        self.tab_widget.setCurrentIndex(0)


    def weigher_tabUI(self):
        self.tab3 = QWidget()
        self.tab_widget.addTab(self.tab3, 'Weigher')
        self.tab_widget.setTabText(2, 'Weigher')
        self.main_layout03 = QVBoxLayout()
        self.tab3.setLayout(self.main_layout03)
        self.firstlayout03 = QHBoxLayout()
        self.main_layout03.addLayout(self.firstlayout03)
        self.secondlayout03 = QHBoxLayout()
        self.secondlayout03.setAlignment(Qt.AlignCenter)
        self.main_layout03.addLayout(self.secondlayout03)
        # first layout, left layout
        self.firstlayout03_left = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_left)
        self.textedit03 = QTextEdit()
        self.firstlayout03_left.addWidget(self.textedit03)
        self.firstlayout03_right = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_right)
        # first layout , right layout
        self.firstlayout03_right = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_right)
        self.cbox03 = QComboBox()
        self.firstlayout03_right.addWidget(self.cbox03)
        self.button03_open = QPushButton('open')
        self.button03_open.clicked.connect(self.serial_open03)
        self.firstlayout03_right.addWidget(self.button03_open)
        self.button03_close = QPushButton('close')
        self.button03_close.setEnabled(False)
        self.button03_close.clicked.connect(self.serial_close03)
        self.firstlayout03_right.addWidget(self.button03_close)
        self.button03_clear = QPushButton('clear text')
        self.button03_clear.clicked.connect(self.clear_textedit03)
        self.firstlayout03_right.addWidget(self.button03_clear)
        self.button03_refresh = QPushButton('refresh')
        self.button03_refresh.clicked.connect(self.device_refresh03)
        self.firstlayout03_right.addWidget(self.button03_refresh)
        # second layout
        self.button03_backward = QPushButton('backward')
        self.button03_backward.clicked.connect(self.backward03)
        self.secondlayout03.addWidget(self.button03_backward)
        self.button03_forward = QPushButton('confirm')
        self.button03_forward.clicked.connect(self.forward03)
        self.secondlayout03.addWidget(self.button03_forward)


    def serial_open03(self):
        self.serial.setPortName(self.cbox03.currentText())  # passing name such as 'COM1'
        if self.serial.open(QIODevice.ReadOnly):
            # self.serial.setDataTerminalReady(True)  # setting the specific pin to the high-value voltage;
            # print('The reconnection to the serial port is successful.')
            self.button03_open.setEnabled(False)
            self.button03_close.setEnabled(True)
        else:
            reply = QMessageBox.warning(self, 'Warning', 'The reconnection to the serial port is failed.', QMessageBox.Ok)


    def serial_acceptData03(self):
        data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
        data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
        # print('The length of data is %s and the value part is %s' %(len(data2), data2))
        self.textedit03.insertPlainText(data2)
        discard = self.serial.readAll()


    def serial_close03(self):
        self.serial.close()
        self.button03_open.setEnabled(True)
        self.button03_close.setEnabled(False)


    def clear_textedit03(self):
        self.textedit03.clear()


    def device_refresh03(self):
        self.serialPort_list = []
        self.cbox03.clear()
        self.serialPort_list = QSerialPortInfo.availablePorts()
        for port in self.serialPort_list:
            # print(port.portName())
            self.cbox03.addItem(port.portName())


    def forward03(self):
        """
        Currently, this will get the information from those comboBox and record them into the new cfg file.
        :return:
        """
        message = """
        the number of the item camera: %s
        the number of the user camera: %s
        the number of the serial port: %s
        """ %(self.cbox01.currentIndex(), self.cbox02.currentIndex(), self.cbox03.currentText())
        reply = QMessageBox.question(self, 'Save your selection',message, QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # self.cf.set('cam_item','cam_num',str(self.cbox01.currentIndex()))
            # self.cf.set('cam_user','cam_num',str(self.cbox02.currentIndex()))
            # self.cf.set('weigher','port_name',self.cbox03.currentText())
            self.cf['cam_item']['cam_num'] = str(self.cbox01.currentIndex())
            self.cf['cam_user']['cam_num'] = str(self.cbox02.currentIndex())
            self.cf['weigher']['port_name'] = self.cbox03.currentText()
            self.close()
        else:
            # If user click on the X button, the reply also is the QMessageBox.No;
            # print('no')
            pass


    def backward03(self):
        self.tab_widget.setCurrentIndex(1)


    def closeEvent(self, event):
        for thread in self.thread_list:
            thread.status = False
            thread.capture.release()
        self.thread_list = []
        self.serial.close()
        with open(self.cfg_path, 'w') as configfile:
            self.cf.write(configfile)
        super(UserGuide03, self).closeEvent(event)


class UserGuide03linux01(UserGuide03):
    def __init__(self, cfg_path='Klas2.cfg'):
        super(UserGuide03linux01, self).__init__(cfg_path=cfg_path)

    def comboBox_changed01(self, current_index):
        self.thread_list[self.last_index01].update.disconnect(self.refresh_label01)
        self.thread_list[current_index].update.connect(self.refresh_label01)
        self.last_index01 = current_index

    def comboBox_changed02(self, current_index):
        self.thread_list[self.last_index02].update.disconnect(self.refresh_label02)
        self.thread_list[current_index].update.connect(self.refresh_label02)
        self.last_index02 = current_index


class UserGuide03_1(QDialog):
    """
    Compared with the UserGuide01 class, the main difference is that it will read the original cfg file;
    Another difference is that it saves the configuration into another cfg file (closeEvent);
    Compared with the UserGuide02 class, the UserGuide02_1 class uses self.thread_list rather than self.camera_list;
    Compared with the UserGuide02 class, the UserGuide02_1 class uses signal connection and disconnection to display different frame!
    Compared with the UserGuide02 class, the UserGuide02_1 class uses readAll() at the end of the serial_acceptData03 function.
    Compared with the UserGuide03 class, the UserGuide03 class adds extra window for the door controller;
    """
    def __init__(self, cfg_path='Klas2.cfg', parent=None):
        super(UserGuide03_1, self).__init__(parent)
        self.cfg_path = cfg_path
        self.width = 600
        self.height = 600
        self.x = 700
        self.y = 300
        # these functions come from QWidget;
        self.move(self.x, self.y)
        self.setFixedSize(self.width, self.height)
        # self.setStyleSheet('background-color: rgb(64,64,64);')
        # self.setWindowFlags()
        self.setWindowTitle('User Guide')

        # layout management
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self.camera_tab1UI()
        self.camera_tab2UI()
        self.weigher_tabUI()
        self.door_controller_tabUI()

        # config
        self.cf = configparser.ConfigParser()
        self.cf.read(cfg_path)
        # print(self.cf.sections())

        # cameras
        camera_device = QCamera()  # You have to declare QCamera object before using QCameraInfo.availableCameras()
        self.thread_list = []
        for index, cam in enumerate(QCameraInfo.availableCameras()):
            a = MyCameraThread1_2(cv2.VideoCapture(index))
            self.thread_list.append(a)
            a.start()


        # serial port
        self.serialPort_list = QSerialPortInfo.availablePorts()
        for port in self.serialPort_list:
            # print(port.portName())
            self.cbox03.addItem(port.portName())
            self.cbox04.addItem(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setBaudRate(9600)
        self.serial.setDataBits(QSerialPort.DataBits(8))
        self.serial.setStopBits(QSerialPort.StopBits(1))
        self.serial.readyRead.connect(self.serial_acceptData03)

        # the default work
        self.last_index01 = 0
        self.last_index02 = 0
        if len(self.thread_list) > 0:
            self.thread_list[0].update.connect(self.refresh_label01)
            self.thread_list[0].update.connect(self.refresh_label02)
            for index, item in enumerate(self.thread_list):
                self.cbox01.insertItem(index, '%s' %index)
                self.cbox02.insertItem(index, '%s' %index)
        else:
            self.label01.setText("No camera found! Please check for the camera and then click the 'refresh' button")
            self.label02.setText("No camera found! Please check for the camera and then click the 'refresh' button")

        self.cbox02.currentIndexChanged.connect(self.comboBox_changed02)
        self.cbox01.currentIndexChanged.connect(self.comboBox_changed01)

    def camera_tab1UI(self):
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, 'Camera for Item')
        self.tab_widget.setTabText(0, 'Camera for Item')
        self.main_layout01 = QVBoxLayout()
        self.tab1.setLayout(self.main_layout01)
        self.firstlayout01 = QHBoxLayout()
        self.main_layout01.addLayout(self.firstlayout01)
        self.secondlayout01 = QHBoxLayout()
        self.secondlayout01.setAlignment(Qt.AlignCenter)
        self.main_layout01.addLayout(self.secondlayout01)
        # first layout
        self.label01 = QLabel()
        self.label01.setScaledContents(True)
        self.firstlayout01.addWidget(self.label01)
        self.firstlayout01_right = QVBoxLayout()
        self.firstlayout01.addLayout(self.firstlayout01_right)
        self.cbox01 = QComboBox()
        self.firstlayout01_right.addWidget(self.cbox01)
        self.button01_refresh = QPushButton('refresh')
        self.button01_refresh.clicked.connect(self.device_refresh01)
        self.firstlayout01_right.addWidget(self.button01_refresh)
        # second layout
        # self.button01_backward = QPushButton('backward')
        # self.secondlayout01.addWidget(self.button01_backward)
        self.button01_forward = QPushButton('forward')
        self.button01_forward.clicked.connect(self.forward01)
        self.secondlayout01.addWidget(self.button01_forward)

    def comboBox_changed01(self, current_index):
        """
        What if the camera does not exist anymore? The question is how can I detect that.
        By testing, cv2.VideoCapture.isOpened() function cannot tell you whether the camera is exists.
        :param current_index:
        :return:
        """
        print('comboBox_changed01 begins')
        if len(QCameraInfo.availableCameras()) == len(self.thread_list):
            self.thread_list[self.last_index01].update.disconnect(self.refresh_label01)
            self.thread_list[current_index].update.connect(self.refresh_label01)
            self.last_index01 = current_index
            print('comboBox_changed01 ends')
        else:
            print('The camera with index %s is closed (comboBox_changed01 end).' % current_index)
            self.device_refresh01()

    def refresh_label01(self, img):
        # print('refresh_label01 begins')
        if type(img) == QImage:
            self.label01.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage
        # print('refresh_label01 ends')

    def device_refresh01(self):
        print('device_refresh01 begins')
        self.cbox02.currentIndexChanged.disconnect(self.comboBox_changed02)
        self.cbox01.currentIndexChanged.disconnect(self.comboBox_changed01)
        for thread in self.thread_list:
            thread.status = False
            thread.capture.release()
        self.thread_list = []
        for index, cam in enumerate(QCameraInfo.availableCameras()):
            a = MyCameraThread1_2(cv2.VideoCapture(index))
            self.thread_list.append(a)
            a.start()
        self.cbox01.clear()
        self.cbox02.clear()

        self.last_index01 = 0
        self.last_index02 = 0
        if len(self.thread_list) > 0:
            self.thread_list[0].update.connect(self.refresh_label01)
            self.thread_list[0].update.connect(self.refresh_label02)
            for index, item in enumerate(self.thread_list):
                self.cbox01.insertItem(index, '%s' %index)
                self.cbox02.insertItem(index, '%s' %index)
        else:
            self.label01.setText("No camera found! Please check for the camera and then click the 'refresh' button")
            self.label02.setText("No camera found! Please check for the camera and then click the 'refresh' button")
        self.cbox02.currentIndexChanged.connect(self.comboBox_changed02)
        self.cbox01.currentIndexChanged.connect(self.comboBox_changed01)
        print('device_refresh01 ends')

    def forward01(self):
        self.tab_widget.setCurrentIndex(1)

    def camera_tab2UI(self):
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, 'Camera for User')
        self.tab_widget.setTabText(1, 'Camera for User')
        self.main_layout02 = QVBoxLayout()
        self.tab2.setLayout(self.main_layout02)
        self.firstlayout02 = QHBoxLayout()
        self.main_layout02.addLayout(self.firstlayout02)
        self.secondlayout02 = QHBoxLayout()
        self.secondlayout02.setAlignment(Qt.AlignCenter)
        self.main_layout02.addLayout(self.secondlayout02)
        # first layout
        self.label02 = QLabel()
        self.label02.setScaledContents(True)
        self.firstlayout02.addWidget(self.label02)
        self.firstlayout02_right = QVBoxLayout()
        self.firstlayout02.addLayout(self.firstlayout02_right)
        self.cbox02 = QComboBox()

        self.firstlayout02_right.addWidget(self.cbox02)
        self.button02_refresh = QPushButton('refresh')
        self.button02_refresh.clicked.connect(self.device_refresh01)
        self.firstlayout02_right.addWidget(self.button02_refresh)
        # second layout
        self.button02_backward = QPushButton('backward')
        self.button02_backward.clicked.connect(self.backward02)
        self.secondlayout02.addWidget(self.button02_backward)
        self.button02_forward = QPushButton('forward')
        self.button02_forward.clicked.connect(self.forward02)
        self.secondlayout02.addWidget(self.button02_forward)

    def comboBox_changed02(self, current_index):
        print('comboBox_changed02 begins')
        if len(QCameraInfo.availableCameras()) == len(self.thread_list):
            self.thread_list[self.last_index02].update.disconnect(self.refresh_label02)
            self.thread_list[current_index].update.connect(self.refresh_label02)
            self.last_index02 = current_index
            print('comboBox_changed02 ends')
        else:
            print('The camera with index %s is closed (comboBox_changed02 end).' % current_index)
            self.device_refresh01()

    def refresh_label02(self, img):
        # print('refresh_label02 begins')
        if type(img) == QImage:
            self.label02.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage
        # print('refresh_label02 ends')

    def forward02(self):
        self.tab_widget.setCurrentIndex(2)

    def backward02(self):
        self.tab_widget.setCurrentIndex(0)

    def weigher_tabUI(self):
        self.tab3 = QWidget()
        self.tab_widget.addTab(self.tab3, 'Weigher')
        self.tab_widget.setTabText(2, 'Weigher')
        self.main_layout03 = QVBoxLayout()
        self.tab3.setLayout(self.main_layout03)
        self.firstlayout03 = QHBoxLayout()
        self.main_layout03.addLayout(self.firstlayout03)
        self.secondlayout03 = QHBoxLayout()
        self.secondlayout03.setAlignment(Qt.AlignCenter)
        self.main_layout03.addLayout(self.secondlayout03)
        # first layout, left layout
        self.firstlayout03_left = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_left)
        self.textedit03 = QTextEdit()
        self.firstlayout03_left.addWidget(self.textedit03)
        self.firstlayout03_right = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_right)
        # first layout , right layout
        self.firstlayout03_right = QVBoxLayout()
        self.firstlayout03.addLayout(self.firstlayout03_right)
        self.cbox03 = QComboBox()
        self.firstlayout03_right.addWidget(self.cbox03)
        self.button03_open = QPushButton('open')
        self.button03_open.clicked.connect(self.serial_open03)
        self.firstlayout03_right.addWidget(self.button03_open)
        self.button03_close = QPushButton('close')
        self.button03_close.setEnabled(False)
        self.button03_close.clicked.connect(self.serial_close03)
        self.firstlayout03_right.addWidget(self.button03_close)
        self.button03_clear = QPushButton('clear text')
        self.button03_clear.clicked.connect(self.clear_textedit03)
        self.firstlayout03_right.addWidget(self.button03_clear)
        self.button03_refresh = QPushButton('refresh')
        self.button03_refresh.clicked.connect(self.device_refresh03)
        self.firstlayout03_right.addWidget(self.button03_refresh)
        # second layout
        self.button03_backward = QPushButton('backward')
        self.button03_backward.clicked.connect(self.backward03)
        self.secondlayout03.addWidget(self.button03_backward)
        self.button03_forward = QPushButton('forward')
        self.button03_forward.clicked.connect(self.forward03)
        self.secondlayout03.addWidget(self.button03_forward)

    def serial_open03(self):
        self.serial.setPortName(self.cbox03.currentText())  # passing name such as 'COM1'
        if self.serial.open(QIODevice.ReadOnly):
            # self.serial.setDataTerminalReady(True)  # setting the specific pin to the high-value voltage;
            # print('The reconnection to the serial port is successful.')
            self.button03_open.setEnabled(False)
            self.button03_close.setEnabled(True)
        else:
            reply = QMessageBox.warning(self, 'Warning', 'The reconnection to the serial port is failed.', QMessageBox.Ok)

    def serial_acceptData03(self):
        data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
        data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
        # print('The length of data is %s and the value part is %s' %(len(data2), data2))
        self.textedit03.insertPlainText(data2)
        discard = self.serial.readAll()

    def serial_close03(self):
        self.serial.close()
        self.button03_open.setEnabled(True)
        self.button03_close.setEnabled(False)

    def clear_textedit03(self):
        self.textedit03.clear()

    def device_refresh03(self):
        self.serialPort_list = []
        self.cbox03.clear()
        self.serialPort_list = QSerialPortInfo.availablePorts()
        for port in self.serialPort_list:
            # print(port.portName())
            self.cbox03.addItem(port.portName())

    def forward03(self):
        self.tab_widget.setCurrentIndex(3)

    def backward03(self):
        self.tab_widget.setCurrentIndex(1)

    def door_controller_tabUI(self):
        self.tab4 = QWidget()
        self.tab_widget.addTab(self.tab4, 'Door controller')
        self.tab_widget.setTabText(3, 'Door controller')
        self.main_layout04 = QVBoxLayout()
        self.tab4.setLayout(self.main_layout04)
        self.firstlayout04 = QHBoxLayout()
        self.main_layout04.addLayout(self.firstlayout04)
        self.secondlayout04 = QHBoxLayout()
        self.secondlayout04.setAlignment(Qt.AlignCenter)
        self.main_layout04.addLayout(self.secondlayout04)
        # first layout
        self.cbox04 = QComboBox()
        self.firstlayout04.addWidget(self.cbox04)

        # second layout
        self.button04_backward = QPushButton('backward')
        self.button04_backward.clicked.connect(self.backward04)
        self.secondlayout04.addWidget(self.button04_backward)
        self.button04_forward = QPushButton('confirm')
        self.button04_forward.clicked.connect(self.forward04)
        self.secondlayout04.addWidget(self.button04_forward)

    def backward04(self):
        self.tab_widget.setCurrentIndex(2)

    def forward04(self):
        """
        Currently, this will get the information from those comboBox and record them into the new cfg file.
        :return:
        """
        message = """
        the number of the item camera: %s
        the number of the user camera: %s
        the name of the serial port: %s
        the name of the door controller: %s
        """ %(self.cbox01.currentIndex(), self.cbox02.currentIndex(), self.cbox03.currentText(), self.cbox04.currentText())
        reply = QMessageBox.question(self, 'Save your selection',message, QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # self.cf.set('cam_item','cam_num',str(self.cbox01.currentIndex()))
            # self.cf.set('cam_user','cam_num',str(self.cbox02.currentIndex()))
            # self.cf.set('weigher','port_name',self.cbox03.currentText())
            self.cf['cam_item']['cam_num'] = str(self.cbox01.currentIndex())
            self.cf['cam_user']['cam_num'] = str(self.cbox02.currentIndex())
            self.cf['weigher']['port_name'] = self.cbox03.currentText()
            self.cf['door_controller']['port_name'] = self.cbox04.currentText()
            self.close()
        else:
            # If user click on the X button, the reply also is the QMessageBox.No;
            # print('no')
            pass

    def closeEvent(self, event):
        for thread in self.thread_list:
            thread.status = False
            thread.capture.release()
        self.thread_list = []
        self.serial.close()
        with open(self.cfg_path, 'w') as configfile:
            self.cf.write(configfile)
        super(UserGuide03_1, self).closeEvent(event)


class UserGuide03_1linux01(UserGuide03_1):
    def __init__(self, cfg_path='Klas2.cfg'):
        super(UserGuide03_1linux01, self).__init__(cfg_path=cfg_path)

    def comboBox_changed01(self, current_index):
        self.thread_list[self.last_index01].update.disconnect(self.refresh_label01)
        self.thread_list[current_index].update.connect(self.refresh_label01)
        self.last_index01 = current_index

    def comboBox_changed02(self, current_index):
        self.thread_list[self.last_index02].update.disconnect(self.refresh_label02)
        self.thread_list[current_index].update.connect(self.refresh_label02)
        self.last_index02 = current_index


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.a = UserGuide03_1linux01()
        # self.a.show()
        result = self.a.exec()  # This will block the main process to execute the commands below;
        # print(type(result))
        # print(result)
        # self.setCentralWidget(self.a)
        # print('Your result is %s' %result) # normal this is 0 indicating the normal exit of exec() function.


# 外部接口调用
class UserGuide():
    def __init__(self, cfg_path='Config.cfg'):
        UserGuide03_1linux01(cfg_path=cfg_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    sys.exit(app.exec_())

