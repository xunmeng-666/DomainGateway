# -*- coding:utf-8-*-
import os
import running
import time
from conf.config import *


PATH = os.path.dirname(__file__)


class Install(object):
    def __init__(self):
        self.ip = ip
        self.port = port
        self.user = username
        self.passwd = password
        self.email = email

    def python(self):

        print('安装Python3')
        os.system("yum install -y $cat %s" %(os.path.join(PATH,'yum-requirements')))

    def uppip(self):
        print('更新PIP版本')
        os.system("pip3 install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com --upgrade pip")

    def pip(self):
        print('PIP安装Python库')
        os.system("pip3 install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com -r %s" % (os.path.join(PATH,
                                                                                                                        "requirements")))

    def sync(self):
        print('生成数据表')
        os.system("python3 %s makemigrations" %(os.path.join(PATH,'manage.py')))
        os.system("python3 %s migrate" %(os.path.join(PATH,'manage.py')))

    def createuser(self):
        try:
            from django.contrib.auth.models import User
            print('初始化登录用户')
            time.sleep(2)
            user = User.objects.create_superuser(username=self.user,password=self.passwd,email=self.email,is_staff=True)
            user.save()
            print('默认用户名:%s，密码:%s，邮箱:%s' %(self.user,self.passwd,self.email))
        except Exception:
            pass

    def service(self):
        os.system("sh %s start" %(os.path.join(PATH,'services.sh')))


    def main(self):
        self.python()
        self.uppip()
        self.pip()
        self.sync()
        self.createuser()
        self.service()
        print('请手动运行命令创建管理员用户: python3 manage.py createsuperuser')

if __name__ in "__main__":
    Install().main()


def do_install(pkgs):
    try:
        import pip._internal as pip_new
    except ImportError:
        error_no_pip()
    return pip_new.main(['install'] + pkgs)


def do_uninstall(pkgs):
    try:
        import pip._internal as pip_new
    except ImportError:
        error_no_pip()
    return pip_new.main(['uninstall', '-y'] + pkgs)