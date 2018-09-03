# -*- coding: utf-8 -*-
"""
It makes Brindley friendly to users;
author = hobin;
email = '627227669@qq.com';
"""
import sys
import cv2
import mysql.connector
from PyQt5.QtCore import QIODevice
from PyQt5.QtMultimedia import QCameraInfo, QCamera
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from tensorflow.python.client import device_lib
import requests

def necessaryCheck(**kwargs):
    """
    It is used after the configuration executed by the class from the ConfiguringModule.py file;
    Currently, every checking is designed to throw the SystemExit exception if something does not go as expected;
    :param kwargs: the dictionary created by the class from the ConfiguringModule.py file;
    :return:
    """
    check_status = False

    # check for the cameras to reduce the camera issue when they are used.
    if kwargs['necessary_check']['camera_check'] == '1':
        print('start to check cameras')
        check01 = cameraCheck(**kwargs)

    # check for the weigher to avoid the corresponding issue when they are used.
    if kwargs['necessary_check']['weigher_check'] == '1':
        print('start to check the weigher')
        check02 = weigherCheck(**kwargs)

    # check for the database
    if kwargs['necessary_check']['database_check'] == '1':
        print('start to check the database')
        check03 = databaseCheck(**kwargs)

    # check for the Internet service
    if kwargs['necessary_check']['internet_check'] == '1':
        print('start to check the Internet')
        check04 = _InternetCheck()

    # check for the gpu
    if kwargs['necessary_check']['gpu_check'] == '1':
        print('start to check the GPU')
        check99 = gpuCheck()

    check_status = True
    print('All equipments are checked.')
    return check_status


def necessaryCheck_linux(self, **kwargs):
    """
    It is used after the configuration executed by the class from the ConfiguringModule.py file;
    Currently, every checking is designed to throw the SystemExit exception if something does not go as expected;
    :param kwargs: the dictionary created by the class from the ConfiguringModule.py file;
    :return:
    """
    self.check_status = False

    # check for the cameras to reduce the camera issue when they are used.
    if kwargs['necessary_check']['camera_check'] == '1':
        print('start to check cameras')
        check01 = cameraCheck(**kwargs)

    # check for the weigher to avoid the corresponding issue when they are used.
    if kwargs['necessary_check']['weigher_check'] == '1':
        print('start to check the weigher')
        check02 = weigherCheck_linux01(**kwargs)

    # check for the database
    if kwargs['necessary_check']['database_check'] == '1':
        print('start to check the database')
        check03 = databaseCheck(**kwargs)

    # check for the Internet service
    if kwargs['necessary_check']['internet_check'] == '1':
        print('start to check the Internet')
        check04 = _InternetCheck()

    # check for the gpu
    if kwargs['necessary_check']['gpu_check'] == '1':
        print('start to check the GPU')
        check99 = gpuCheck()

    self.check_status = True
    print('All equipments are checked.')
    return self.check_status


def cameraCheck(**kwargs):
    check_status = False
    if kwargs['operating_mode']['cam_path_used'] == '1':
        camera_user = kwargs['cam_user']['cam_path']
        camera_item = kwargs['cam_item']['cam_path']
    else:
        camera_user = int(kwargs['cam_user']['cam_num'])
        camera_item = int(kwargs['cam_item']['cam_num'])
    camera_device = QCamera()  # You have to declare QCamera object before using QCameraInfo.availableCameras()
    camera_list = QCameraInfo.availableCameras()
    # print(camera_list)  # the result is like [<PyQt5.QtMultimedia.QCameraInfo object at 0x0000029C36641828>, <PyQt5.QtMultimedia.QCameraInfo object at 0x0000029C36641898>]
    if len(camera_list) < 2:
        # print('Camera problem happens!')
        sys.exit('Camera problem: available cameras are not enough!')  # sys.exit just throws an exception.
    else:
        # try to use cameras to see whether there is some unknown issues.
        cap0 = cv2.VideoCapture(camera_item)
        cap1 = cv2.VideoCapture(camera_user)
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()
        cap0.release()
        cap1.release()
        if not (ret0 and ret1):
            sys.exit('Camera problem: frame cannot be read successfully. Please take them off and then plugs them in.')

    check_status = True
    return check_status


def weigherCheck(**kwargs):
    check_status = False
    port_name = kwargs['weigher']['port_name']
    baud_rate = int(kwargs['weigher']['baud_rate'])
    data_bits = int(kwargs['weigher']['data_bits'])
    stop_bits = int(kwargs['weigher']['stop_bits'])
    list_serialPort = QSerialPortInfo.availablePorts()
    # print(list_serialPort)  # the result is like <PyQt5.QtSerialPort.QSerialPortInfo object at 0x00000261AA5C1908>
    if len(list_serialPort) < 1:
        sys.exit('Weigher problem: weigher is missing')
    else:
        # try to use weigher to see whether there is some unknown issues.
        serial = QSerialPort()  # It is the subclass of the QIODevice class;
        serial.setPortName(port_name)  # passing name such as 'COM1'
        serial.setBaudRate(int(baud_rate))
        serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        if serial.open(QIODevice.ReadOnly):
            # The QSerial.waitForReadyRead function blocks until new data is available for reading and the readyRead() signal has been emitted.
            # This function returns true if the readyRead() signal is emitted and there is new data available for reading;
            # Otherwise this function returns false (if an error occurred or the operation timed out).
            if serial.waitForReadyRead(8000):  # the unit is millisecond;
                data1 = serial.readLine()
                data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
                data3 = float(data2[1:-4])  # This will raise error if the data can not be converted successfully.
            else:
                sys.exit('Weigher problem: no data received from the weigher.')
            serial.close()
        else:
            sys.exit('Weigher problem: the connection to the specific weigher fails. Please check the port name.')

    check_status = True
    return check_status


def weigherCheck_linux01(**kwargs):
    """
    Compared with weigherCheck, the main difference is the way to try converting data;
    :param kwargs:
    :return:
    """
    check_status = False
    port_name = kwargs['weigher']['port_name']
    baud_rate = int(kwargs['weigher']['baud_rate'])
    data_bits = int(kwargs['weigher']['data_bits'])
    stop_bits = int(kwargs['weigher']['stop_bits'])
    list_serialPort = QSerialPortInfo.availablePorts()
    # print(list_serialPort)  # the result is like <PyQt5.QtSerialPort.QSerialPortInfo object at 0x00000261AA5C1908>
    if len(list_serialPort) < 1:
        sys.exit('Weigher problem: weigher is missing')
    else:
        # try to use weigher to see whether there is some unknown issues.
        serial = QSerialPort()  # It is the subclass of the QIODevice class;
        serial.setPortName(port_name)  # passing name such as 'COM1'
        serial.setBaudRate(int(baud_rate))
        serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        if serial.open(QIODevice.ReadOnly):
            # The QSerial.waitForReadyRead function blocks until new data is available for reading and the readyRead() signal has been emitted.
            # This function returns true if the readyRead() signal is emitted and there is new data available for reading;
            # Otherwise this function returns false (if an error occurred or the operation timed out).
            if serial.waitForReadyRead(8000):  # the unit is millisecond;
                discard = serial.readAll()
                status_data_convert = True
                convert_times = 0
                can_readline_times = 0
                while status_data_convert:
                    if serial.waitForReadyRead(500):
                        if serial.canReadLine():
                            data1 = serial.readLine()
                            data2 = data1.data().decode(
                                'ascii')  # converting the data type to str (the original string);
                            try:
                                data3 = float(data2[1:-4])  # This will raise error if the data can not be converted successfully.
                                status_data_convert = False
                            except BaseException:
                                convert_times = convert_times + 1
                                print('Trying to convert the data fails with total %s times.' % convert_times)
                                if convert_times > 29:
                                    sys.exit('Weigher problem: the string data given by weigher can not be converted to the float data successfully.')
                        else:
                            can_readline_times = can_readline_times + 1
                            print('canReadLine fails with total %s times.' %can_readline_times)
                            if can_readline_times > 29:
                                sys.exit('Weigher problem: there is no readLine signal too many times.')
                    else:
                        convert_times = convert_times + 1
                        print('waitForReadyRead fails with total %s times.' % convert_times)
                        if convert_times > 29:
                            sys.exit('Weigher problem: the string data given by weigher can not be converted to the float data successfully.')
            else:
                sys.exit('Weigher problem: no data received from the weigher.')
            serial.close()
        else:
            sys.exit('Weigher problem: the connection to the specific weigher fails. Please check the port name.')

    check_status = True
    return check_status


def gpuCheck():
    check_status = False
    processor_list = device_lib.list_local_devices() # the data type is a list
    for unit in processor_list:
        # print(type(unit)) # it is <class 'tensorflow.core.framework.device_attributes_pb2.DeviceAttributes'>
        # print(unit)
        if unit.device_type == 'GPU':
            check_status = True
            break
    if not check_status:
        sys.exit('GPU problem: the gpu is missing')
    return check_status


def databaseCheck(**kwargs):
    check_status = False
    mysql_config = {
        'user': kwargs['db']['db_user'],
        'password': kwargs['db']['db_pass'],
        'port': int(kwargs['db']['db_port']),
        'host': kwargs['db']['db_host'],
        'database': kwargs['db']['db_database']
    }
    try:
        conn = mysql.connector.connect(
            **mysql_config)  # if the connection fails, it will automatically raise the specific exception.
        cursor = conn.cursor()
        cursor.execute('select * from storegoods limit 5')
        result = cursor.fetchall()
        # print(result)
        cursor.close()
        conn.close()
        check_status = True
    except mysql.connector.errors.InterfaceError:
        sys.exit('MySQL problem: please check whether the mysql service is open.')
    except BaseException as e:
        sys.exit('MySQL problem: other problem occurs and please find the administrator.')
    return check_status


def _InternetCheck():
    check_status = False

    try:
        resp = requests.get('http://sys.commaai.cn/', timeout=8)
        #check_status = True
    except requests.exceptions.ConnectTimeout:
        sys.exit('Network problem: 8 seconds pass and there is no response from our server.')
    except BaseException as e:
        sys.exit('Network problem: please check whether the Internet service is open or find the administrator.')
    check_status = True
    return check_status


def cameraGuide():
    pass


if __name__ == '__main__':
    config_dict = {
        'cam_user': {'cam_num':'0'},
        'cam_item': {'cam_num': '1'},
        'weigher': {'port_name':'COM3','baud_rate':'9600','data_bits':'8','stop_bits':'1'},
        'db':{'db_port' : 3306,'db_host' : '127.0.0.1','db_user' : 'root','db_pass' : 'commaai2017','db_database' : 'hobin'},
        'necessary_check':{'check_required':'1','camera_check':'1','weigher_check':'1','gpu_check':'1','database_check':'1','internet_check':'1'}
    }
    necessaryCheck(**config_dict)
    # gpuCheck()
    # databaseCheck(**config_dict)
    # _InternetCheck()

