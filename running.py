# -*- coding:utf-8-*-
import os
import time
from conf.config import *


PATH = os.path.dirname(__file__)
class PreSetup(object):
    def __init__(self):
        self.ip = ip
        self.port = port
        self.user = username
        self.passwd = password
        self.email = email

    def _start(self):
        os.system("nohup python3 manage.py runserver %s:%s &" % (self.ip, self.port))
        return True
    def main(self):
        self._start()

if __name__ in "__main__":
    PreSetup().main()