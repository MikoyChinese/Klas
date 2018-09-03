# -*- coding: utf-8 -*-
"""
Comma Payment Software
"""
import Device

from PyQt5.QtCore import QObject

from configModule import Config
from loggingModule import MyLogging

class PaymentSystem_klas(QObject):
    def __init__(self, **kwargs):
        # Parent and self object init.
        super(PaymentSystem_klas, self).__init__()

        # Start to logging:
        self.mylogging = MyLogging(logger_name='user')
        self.mylogger = self.mylogging.logger

        # Read configuration of <Config.cfg> Payment Software.
        self.basic = Config(cfg_path='Config.cfg')
        self.config = self.basic.out_config()

        #
        self.cam_user = Device.BaseCamera(cam_name=self.config['cam_user'])
        self.cam_item = Device.BaseCamera(cam_name=self.config['cam_item'])
        self.weigher = Device.Weigher(**self.config['weigher'])
        self.door_controller = Device.Weigher(**self.config['door_controller'])
