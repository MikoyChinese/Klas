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

        # 1.Start to logging:
        self.mylogging = MyLogging(logger_name='user')
        self.mylogger = self.mylogging.logger

        # 2.Read configuration of <Config.cfg> Payment Software.
        self.basic = Config(cfg_path='Config.cfg')
        # Please don't edit this confile, it's created by <Config Class>
        self.config = self.basic.out_config()

        # 3.Device Self Check.

        # 4.Initialize Device.
        self.cam_user = Device.BaseCamera(cam_name='cam_user')
        self.cam_item = Device.BaseCamera(cam_name='cam_item')
        self.weigher = Device.Weigher(port_name='weigher')
        self.door_controller = Device.Weigher(port_name='door_controller')
