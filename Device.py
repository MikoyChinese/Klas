# -*- coding: utf-8 -*-
"""
Author: MikoyChinese
Github: github.com/MikoyChinese
Devices:
        - cam_user: [cam_path]
        - cam_item: [cam_path]
        - cam_item2: [cam_path]
        - weigher: [port_name] [baud_rate] [data_bits][stop_bits]
        - door_controller: [port_name] [baud_rate] [data_bits][stop_bits]
"""
import cv2, struct
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QByteArray, pyqtSignal, QIODevice, pyqtSlot
from loggingModule import MyLogging
from functools import wraps


class BaseCamera():
    # The basic Camera Class.
    def __init__(self, cam_name=None):
        self.cam_name = cam_name
        self.cam_path = self.cam_name['cam_path']
        self.width = int(self.cam_name['width'])
        self.height = int(self.cam_name['height'])

        self.capture = cv2.VideoCapture(self.cam_path)
        self.capture.set(3, self.width)
        self.capture.set(4, self.height)

        # Logging info
        MyLogging(logger_name='user').logger.info('%s Finished Initializing.' % self.cam_path)

    def read(self):
        _, img = self.capture.read()
        return _, img

    def isOpen(self):
        # Check the Camera whether it is available.
        return self.capture.isOpened()


# Weigher Class
class Weigher():
    def __init__(self, port_name=None, baud_rate=None, data_bits=None,
                 stop_bits=None):
        # Read config
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.data_bits = data_bits
        self.stop_bits = stop_bits

        # Initial
        self.weigher = QSerialPort()  # It is the subclass of the QIODevice class;
        self.weigher.setPortName(self.port_name)  # passing name such as 'COM1'
        self.weigher.setBaudRate(int(self.baud_rate))
        self.weigher.setDataBits(QSerialPort.DataBits(int(self.data_bits)))
        self.weigher.setStopBits(QSerialPort.StopBits(int(self.stop_bits)))

        # Logging module
        self.mylogging = MyLogging(logger_name='user')
        self.mylogger = self.mylogging.logger

    def read(self):
        if self.weigher.canReadLine():
            ascii_data = self.weigher.readLine()
            data = ascii_data.decode('ascii')
            try:
                # The formate of weigher returns datas.
                weigher_data = float(data[1:-4]) * 1000
                return weigher_data
            except BaseException as e:
                self.mylogger.error(e)


# python 的单例模式, 通过关键字@singleton调用.
def singleton(cls):
	instances = {}
	@wraps(cls)
	def getinstance(*args, **kw):
		if cls not in instances:
			instances[cls] = cls(*args, **kw)
		return instances[cls]
	return getinstance


# Door_controller Class
@singleton
class Door():

    templet = b'\x3a\x00\x00\x00\x00\x0d\x0a'
    # int is id of door
    degaussSuccess = pyqtSignal(int)  # 消磁成功
    inOpenDoorSuccess = pyqtSignal(int)  # 进门开门成功
    outOpenDooSuccess = pyqtSignal(int)  # 出门开门成功
    outOpenDooSuccessByUser = pyqtSignal(int)  # 用户手动开门出门
    getDataSingal = pyqtSignal(str)

    def __init__(self, port_name=None, baud_rate=None, data_bits=None,
                 stop_bits=None):
        # Logging module
        self.mylogging = MyLogging(logger_name='user')
        self.mylogger = self.mylogging.logger
        # Configurate door_controller.
        self.door_controller = QSerialPort()
        self.door_controller.setPortName(port_name)
        self.door_controller.setBaudRate(baud_rate)
        self.door_controller.setDataBits(data_bits)
        self.door_controller.setStopBits(stop_bits)
        # Check self.
        self.check()
        # Start to work.
        self.data = QByteArray()
        self.setDataTerminalReady(True)
        self.readyRead.connect(self.acceptData)

    def check(self):
        info = QSerialPortInfo.availablePorts()
        # Checking SerialPort is deeply used.
        if len(info) == 0:
            self.mylogger.error('SerialPort has no availablePorts.')
            self.mylogger.warning('Please check your [weigher] and ['
                                  'door_controller].')
        if self.port_name == None:
            self.mylogger.error('The port_name of [door_controller] is None.')
        # Checking whether the door serial port can open.
        if not self.door_controller.open(QIODevice.ReadWrite):
            self.mylogger.error('Open %s device failed.' % self.door_controller)
            return None

    def byteToInt(strbyte):
        if type(strbyte) == str:
            strbyte = strbyte.encode('UTF-8')
        t = strbyte + b'\x00'
        i = struct.unpack("<h", t)[0]
        return i

    def get_char_bit(char, n):
        return (char >> (8 - n)) & 1

    # get the LRC
    def getLRC(self, cmd):
        tmp = cmd[1] + cmd[2] + cmd[3]
        if (self.get_char_bit(tmp, 1) == 1):
            tmp = ~tmp
        tmp = struct.pack('<h', tmp)[0] + 1
        return tmp

    # add LRC to Cmd
    def addLRC(self, cmd):
        cmd[4] = self.getLRC(cmd)
        return cmd

    def checkLRC(self, cmd):
        if type(cmd) == QByteArray:
            cmd = cmd.data()
        if type(cmd) != bytearray:
            cmd = bytearray(cmd)
        return cmd[4] == self.getLRC(cmd)


    # send data
    @pyqtSlot(int)
    def sendOpenDoorIn(self, doorNumber):
        cmd = bytearray(self.templet)
        cmd[1] = struct.pack('<h', doorNumber)[0]
        cmd[2] = self.byteToInt(b'\xCC')
        self.mylogger.warning([hex(x) for x in bytes(cmd)])
        if self.door_controller.write(self.addLRC(cmd)) == 7:
            return True
        else:
            return False

    @pyqtSlot(int)
    def sendOpenDoorOut(self, doorNumber):
        cmd = bytearray(self.templet)
        cmd[1] = struct.pack('<h', doorNumber)[0]
        cmd[2] = self.byteToInt(b'\xBB')
        self.mylogger.warning([hex(x) for x in bytes(cmd)])
        if self.door_controller.write(self.addLRC(cmd)) == 7:
            return True
        else:
            return False

    @pyqtSlot(int)
    def sendDegauss(self, doorNumber=1):
        cmd = bytearray(self.templet)
        cmd[1] = struct.pack('<h', doorNumber)[0]
        cmd[2] = self.byteToInt(b'\xAA')
        end = self.addLRC(cmd)
        self.mylogger.warning([hex(x) for x in bytes(end)])
        if self.door_controller.write(end) == 7:
            return True
        else:
            return False

    @pyqtSlot()
    def sendZeroWeight(self):
        cmd = b"\x3A\x01\xAB\x00\x54\x0D\x0A"
        if self.door_controller.write(cmd) == 7:
            return True
        else:
            return False

    @pyqtSlot()
    def acceptData(self):
        # print("acceptData",self.data)
        self.data.append(self.door_controller.readAll())  # read all data
        while self.data.length() > 0:
            if self.data.length() >= 7:  # if get a complete data
                for i in range(self.data.length()):
                    if self.data[i] == '\x3a':  # find the SOI
                        tmp = self.data[i:7]  # get a cmd
                        # print("get cmd :",str(tmp.data()))
                        self.mylogger.debug("Get [cmd]: %s" % str(tmp.data()))
                        tmp = self.bytearray(tmp.data())
                        self.data = self.data[i + 7:]  # cut data
                        doorNumber = tmp[1]
                        if self.checkLRC(tmp):  # check LRC
                            if tmp[2] == self.byteToInt(b'\xaa'):
                                # self.degaussTime  = time.time()
                                # print("接收消磁指令反馈 %s" % self.degaussTime)
                                self.mylogger.debug(
                                    "Get degauss Feedback %s" % tmp)
                                self.degaussSuccess.emit(doorNumber)
                            elif tmp[2] == self.byteToInt(b'\xbb'):
                                if tmp[3] == self.byteToInt(b'\x01'):
                                    self.outOpenDooSuccess.emit(doorNumber)
                                elif tmp[3] == self.byteToInt(b'\x02'):
                                    self.outOpenDooSuccessByUser.emit(
                                        doorNumber)
                            elif tmp[2] == self.byteToInt(b'\xcc'):
                                self.inOpenDoorSuccess.emit(doorNumber)

                            stlist = [hex(c) for c in tmp]
                            st = " ".join(stlist)
                            self.getDataSingal.emit(st)
                        else:
                            self.mylogger.error('LRC check fail.')
                        break
            self.data.append(self.readAll())
            break
        print("accept Data finish.")
        self.mylogger.info("Accept door_controller Data finish.")


if __name__ == '__main__':
    cam = {'cam_item': {'cam_path': '/dev/cam_item', 'cam_num': '0', 'width':
        '800', 'height': '600'}}

    cam_item = BaseCamera(cam['cam_item'])

    while 1:
        _, img = cam_item.read()
        cv2.imshow("capture", img)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    cam_item.capture.release()