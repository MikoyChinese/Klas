# -*- coding: utf-8 -*-
"""
    Check the hardware and software.
    Hardware: camera, weigher, door_controller
    Software: internet, api server
"""
from configModule import Config
from Device import BaseCamera


class BaseCheck():
    def __init__(self, config):
        self.necessary_check = config['necessary_check']
        self.check_status = False


class SelfCheck(BaseCheck):
    # This config is reading by Config Module. <config dict>
    def __init__(self, config):
        super(SelfCheck,self).__init__(config)
        self.necessary_check = config['necessary_check']
        self.check_status = False

        if self.necessary_check['camera_check'] == 1:
            pass

    def cameraCheck(self, cam_name):
        cam = BaseCamera(cam_name=cam_name)
        self.check_status = False
        if cam.isOpen():
            self.check_status = True

    def weigherCheck(self):
        pass

    def databaseCheck(self):
        pass

    def _InternetCheck(self):
        pass

    def gpuCheck(self):
        pass



if __name__ == '__main__':
    config = Config(cfg_path='/media/commaai-03/Free/结算台软件/Klas_bread/Config.cfg').config

    check = SelfCheck(config)
    print(check.necessary_check)
    check.cameraCheck(config['cam_item'])
    print(check.check_status)