#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import os
from logging import handlers
from conf.config import logs


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Loger(object):

    def logger_info(self,LOG_INFO,LOG_LEVEL='INFO',log_type='info'):
        logger = logging.getLogger(log_type)
        logger.setLevel(LOG_LEVEL)
        ch = logging.StreamHandler()
        fh = handlers.RotatingFileHandler(logs, maxBytes=4, backupCount=2)
        fh.setLevel(LOG_LEVEL)
        ch.setLevel(LOG_LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        logger.addHandler(ch)
        logger.addHandler(fh)
        logger.info(LOG_INFO)
        logger.removeHandler(ch)
        logger.removeHandler(fh)
        return logger


logger = Loger()