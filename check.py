# -*- coding: utf-8 -*-
"""
    Check the hardware and software.
    Hardware: camera, weigher, door_controller
    Software: internet, api server
"""
import sys

from configModule import Config
from Device import BaseCamera, Weigher
from loggingModule import MyLogging
from PyQt5.QtCore import QIODevice


class BaseCheck():
    def __init__(self, config):
        self.necessary_check = config['necessary_check']
        self.check_status = False


class SelfCheck(BaseCheck):
    # This config is reading by Config.out_config Module. <config dict>
    def __init__(self, cofig):
        super(SelfCheck,self).__init__(config)
        self._config = config
        self._necessary_check = config['necessary_check']
        self.mylogger = MyLogging(logger_name='user').logger
        self._show_cam_item = config['operating_mode']['show_cam_item']
        self.check_status = False

        if int(self.necessary_check['database_check']):
            self.databaseCheck()
        if int(self.necessary_check['internet_check']):
            self._InternetCheck()
        if int(self.necessary_check['gpu_check']):
            self.gpuCheck()



    def cameraCheck(self, cam_object=BaseCamera()):
        if not cam_object.isOpen():
            self.mylogger.error('%s fails inspection [FAILED].' % cam_object.cam_name)


    def weigherCheck(self, weigher_object=Weigher()):
        weigher = weigher_object
        self.weigher = weigher.weigher
        if self.weigher.open(QIODevice.ReadOnly):
            # The QSerial.waitForReadyRead function blocks until new data is available for reading and the readyRead() signal has been emitted.
            # This function returns true if the readyRead() signal is emitted and there is new data available for reading;
            # Otherwise this function returns false (if an error occurred or the operation timed out).

            if self.weigher.waitForReadyRead(8000):  # the unit is millisecond;
                self.weigher.readAll()
                status_data_convert = True
                convert_times = 0
                can_readline_times = 0
                while status_data_convert:
                    if self.weigher.waitForReadyRead(500):
                        if self.weigher.canReadLine():
                            weigher.read()
                            try:
                                # This will raise error if the data can not be converted successfully.
                                status_data_convert = False
                            except BaseException:
                                convert_times = convert_times + 1
                                self.mylogger.warning('[Weigher] is trying to '
                                                      'convert the data '
                                                      'fails with total %s times.' % convert_times)
                                if convert_times > 29:
                                    self.mylogger.error('[Weigher]: the '
                                                        'string data given by weigher can not be converted to the float data successfully.')
                                    sys.exit()
                        else:
                            can_readline_times = can_readline_times + 1
                            self.mylogger.warning('canReadLine fails with total %s '
                                           'times.'
                             %can_readline_times)
                            if can_readline_times > 29:
                                self.mylogger.error('Weigher problem: there is no readLine signal too many times.')
                                sys.exit()
                    else:
                        convert_times = convert_times + 1
                        self.mylogger.warning('waitForReadyRead fails with total %s '
                                       'times.' %
                          convert_times)
                        if convert_times > 29:
                            self.mylogger.error('Weigher problem: the string data given by weigher can not be converted to the float data successfully.')
                            sys.exit()
            else:
                self.mylogger.error('Weigher problem: no data received from the weigher.')
                sys.exit()
            self.weigher.close()
        else:
            self.mylogger.error('Weigher problem: the connection to the specific weigher fails. Please check the port name.')
            sys.exit()

    def databaseCheck(self):
        pass

    def _InternetCheck(self):
        pass

    def gpuCheck(self):
        pass

    # Private parameters.
    @property
    def config(self):
        return self._config

    @property
    def necessary_check(self):
        return self._necessary_check

    @property
    def show_cam_item(self):
        return self._show_cam_item


if __name__ == '__main__':
    config = Config(cfg_path='/media/commaai-03/Free/结算台软件/Klas_bread/Config.cfg').config

    check = SelfCheck(config)
    print(check.necessary_check)
    check.cameraCheck(config['cam_item'])
    print(check.check_status)