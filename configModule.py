# -*- coding: utf-8 -*-
"""
Configure file of Payment software.
"""

import configparser, sys, os, json
from UserGuide import UserGuide
from loggingModule import MyLogging


class BaseConfig(object):
    def __init__(self, cfg_path):
        # 1. Loading config into <self.config dict>
        self.cfg_path = cfg_path
        # Return config['key']['value']
        self.config = self.read_config(self.cfg_path)

    def read_config(self, cfg_path): # Read config date.
        # Create a config dict to save configuration.
        self.config = {}
        cf = configparser.ConfigParser()
        cf.read(cfg_path)
        # Loading config into <config dict>.
        for section in cf.sections():
            self.config[section] = {}
            for value in cf.options(section):
                self.config[section][value] = cf.get(section, value)
        return self.config

class Config(BaseConfig):
    def __init__(self, cfg_path='Config.cfg'):
        # 1.Loading Config
        super(Config, self).__init__(cfg_path)
        # 2.Logging
        self.mylogging = MyLogging(logger_name='user')
        self.mylogger = self.mylogging.logger

        self._need_guide = self.config['operating_mode']['need_guide']
        self._cam_path_used = self.config['operating_mode']['cam_path_used']
        self._necessary_check = self.config['necessary_check']
        self._cam_user = self.config['cam_user']
        self._cam_item = self.config['cam_item']
        self._cam_item2 = self.config['cam_item2']
        self._account = self.config['account']
        # Check Hardware and Software before working starting.
        self.before_work()

    def device_config(self):
        global cam_path_used
        # 1. Camera path config
        if self.config['operating_mode']['cam_path_used'] == '1':
            cam_path_used = True
        else:
            cam_path_used = False

    def before_work(self): # Self-Check before starting working.
        self.mylogger.info('=============== Start Config ===============')
        # To check whether it need to guide.
        if self.config['operating_mode']['need_guide'] == '1':
            user_guide = UserGuide(cfg_path=self.cfg_path)
            reply = user_guide.exec()
            if reply != 0:
                sys.exit('Error happens in user guide, please try again.')
            self.mylogger.info('UserGuide Finished!')

    def out_config(self):
        # Copy a config file.
        config = self.config.copy()
        # List cam_object.
        cam_object = ['cam_user', 'cam_item', 'cam_item2']
        # If cam not used, remove it.
        if not int(config['cam_item2']['is_used']):
            config.pop('cam_item2')
            cam_object.remove('cam_item2')
        if self.cam_path_used:
            for cam in cam_object:
                config[cam].pop('cam_num')
        else:
            for cam in cam_object:
                config[cam]['cam_path'] = config[cam]['cam_num']
        # Creat config file in ./config/config.ini
        dir_path = os.path.join(os.path.dirname(__file__), 'config')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            self.mylogger.info("Create a Folder: %s" % dir_path)
        file = os.path.join(dir_path, 'config.ini')
        with open(file, 'w') as f:
            f.write(str(config))
            self.mylogger.info('Create a New Config to ./config/config.ini!')
        return config

    @property
    def need_guid(self):
        return self._need_guide

    @property
    def cam_path_used(self):
        return self._cam_path_used

    @property
    def necessary_check(self):
        return self._necessary_check

    @property
    def cam_user(self):
        return self._cam_user

    @property
    def cam_item(self):
        return self._cam_item

    @property
    def cam_item2(self):
        return self._cam_item2

    @property
    def account(self):
        return self._account

if __name__ == '__main__':
    s = Config(cfg_path='/media/commaai-03/Free/结算台软件/Klas_bread/Config.cfg')
    s.out_config()