# -*- coding:utf-8-*-
from asset import models
from asset.core.logger import logger
import json
import datetime
from django.utils import timezone



class SaveLog(object):

    def saveFunc(self,log):
        self.save_log_to_db(log)
        self.save_log_to_file(log)
        return True

    def save_log_to_db(self,log):
        '''save logs to db'''
        return models.Logs.objects.create(user=log['user'],
                                          action=log['action'],
                                          content=log['content'],
                                          date=log['date'])

    def save_log_to_file(self,log):
        if log['action'] == 'Info':
            logger.logger_info(log,)
        elif log['action'] == 'Error':
            logger.logger_error(log)

    def log_info(self,user,action,content):
        now_date = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        log = {"date":now_date,"user":user,"action":action,'content':content}
        self.saveFunc(log)
        return True

class ReadLog(object):
    def read_log(self,admin_class,date,user,action):
        now_time = datetime.datetime.now()
        if date:
            end_time = now_time - datetime.timedelta(days=int(date))
        if not date:
            end_time = now_time - datetime.timedelta(days=2000)
        if user == 'null' and action == 'null':
            obj = admin_class.model.objects.filter(date__gt=end_time).values()
        elif user and action == 'null':
            obj = admin_class.model.objects.filter(date__gt=end_time,user=user).values()
        elif action and user == 'null':
            obj = admin_class.model.objects.filter(date__gt=end_time,action=action).values()
        else:
            obj = admin_class.model.objects.filter(date__gt=end_time,user=user,action=action).values()
        _list = []
        for objs in obj:
            if type(objs['date']) is datetime.datetime:
                objs['date'] = objs['date'].strftime("%Y-%m-%d %H:%M:%S")
            _list.append(objs)

        return json.dumps({"data":_list})

savelog = SaveLog()
readlog = ReadLog()