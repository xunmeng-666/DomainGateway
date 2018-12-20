# -*- coding:utf-8-*-
import subprocess
import json
import os
from django.utils.datastructures import MultiValueDictKeyError

class HaproxyFunc(object):
    def __init__(self):
        self.name = None
        self.domain = None
        self.sport = None
        self.ip = None
        self.dport = None
        self.crt = None
        self.config_file = '/etc/haproxy/haproxy.cfg'
        self.statusd = {"status": '', 'info': ''}

    def variable(self,request):
        # 解析request.POST中的value
        self.name = request.POST['name']
        self.domain = request.POST['domain']
        self.sport = request.POST['sport']
        self.ip = request.POST['ip']
        self.dport = request.POST['dport']
        try:
            print('request',request.POST)
            if request.POST['ssl']:
                self.crt = request.POST['ssl']
                self.write(self.https_cfg(),self.config_file)
            else:
                self.write(self.http_cfg(),self.config_file)
        except MultiValueDictKeyError :
            self.write(self.http_cfg(),self.config_file)
        self.shell('systemctl restart haproxy')
        self.checkGFW()

    def savessl(self,file):
        print('file',file)
        filepath = "/etc/haproxy/ssl/%s" %file
        with open(filepath, 'wb') as f:
            for chunks in file.chunks():
                f.write(chunks)
            f.close()
        return filepath

    def https_cfg(self):

        cfg = '''
frontend %s
    bind *:%s
    bind *:443 ssl crt %s
    acl is_http hdr_beg(host) -i ^(%s)$
    use_backend %s_%s if is_http
    
backend %s_%s
    mode http
    balance roundrobin
    server web01 %s:%s  check inter 2000 fall 2 weight 20
    
''' % (self.name, self.sport,self.crt,self.domain, self.name, self.sport,self.name, self.sport, self.ip, self.dport)
        return cfg

    def http_cfg(self):

        cfg = '''
frontend  %s
    bind *:%s
    default_backend %s-%s
    mode tcp
    option tcplog

backend %s-%s
    balance source
    mode tcp
    server  web01 %s:%s check inter 2000 fall 2 weight 20
    
''' % (self.name, self.sport, self.name, self.sport,self.name, self.sport,self.ip,self.dport)
        return cfg

    def defalut_func(self):
        cfg = '''
# Global settings
#---------------------------------------------------------------------
global
    maxconn     20000
    log         /dev/log local0 info
    chroot      /var/lib/haproxy
    pidfile     /var/run/haproxy.pid
    user        haproxy
    group       haproxy
    daemon

    # turn on stats unix socket
    stats socket /var/lib/haproxy/stats

#---------------------------------------------------------------------
# common defaults that all the 'listen' and 'backend' sections will
# use if not designated in their block
#---------------------------------------------------------------------
defaults
    mode                    http
    log                     global
    option                  httplog
    option                  dontlognull
#    option http-server-close
    option forwardfor       except 127.0.0.0/8
    option                  redispatch
    retries                 3
    timeout http-request    10s
    timeout queue           1m
    timeout connect         10s
    timeout client          300s
    timeout server          300s
    timeout http-keep-alive 10s
    timeout check           10s
    maxconn                 20000

listen stats
    bind :9000
    mode http
    stats enable
    stats uri /
        '''
        return cfg

    def write(self,cfg,file):
        self.shell("echo '%s' >> %s" %(cfg,file))
        return True

    def shell(self,cmd):
        returncmd = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        return returncmd

    def checkcfg(self):
        with open(self.config_file,'r') as f:
            if 'global' in f.readlines():
                return True
            return False

    def checkGFW(self):
        firewalld = self.shell("systemctl status firewalld")
        iptables = self.shell("systemctl status iptables")
        if firewalld == 0:
            self.shell("firewall-cmd --zone=public --add-port %s/tcp --permanent" %self.sport)
            self.shell("systemctl reload firewalld")
        if iptables == 0:
            self.shell("iptables -A INPUT -p tcp --dport %s -j ACCEPT" %self.sport)
            self.shell("systemctl reload iptables")
        return True

    def checkservice(self):
        run = self.shell('systemctl status haproxy')
        return run

    def buildcfg(self,admin_class):
        new_file = "%s.bak" %self.config_file
        info = admin_class.model.objects.values()
        self.write(self.defalut_func(),new_file)
        try:
            for obj in info:
                print('obj',obj)
                self.name = obj['name']
                self.sport = obj['sport']
                self.ip = obj['ip']
                self.dport = obj['dport']
                self.domain = obj['domain']
                self.crt = obj['ssl']
                if obj['ssl'] is not None:
                    self.crt = obj['ssl']
                    self.write(self.https_cfg(),new_file)
                self.write(self.http_cfg(),new_file)
            os.remove(self.config_file)
            os.rename(new_file,self.config_file)
            cmd = self.shell("systemctl restart haproxy")
            if cmd == 0:
                return True
            return False
        except KeyError as e:
            pass

class HAFunc(HaproxyFunc):
    # 解析前端指令，返回指令信息

    def status(self,request):
        cmd = self.shell('systemctl status haproxy')
        if cmd.wait() == 0:
            self.statusd['status'] = 'success'
            self.statusd['info'] = '运行'
            return json.dumps(self.statusd)
        self.statusd['status'] = 'error'
        self.statusd['info'] = '停止'
        return json.dumps(self.statusd)

    def display_cfg(self):
        return self.config_file

    def restart(self):
        cmd = self.shell('systemctl restart haproxy')
        if cmd.wait() == 0:
            self.statusd['status'] = 'success'
            self.statusd['info'] = '重启成功'
            return json.dumps(self.statusd)
        self.statusd['status'] = 'info'
        self.statusd['info'] = cmd.stdout.read()
        return json.dumps(self.statusd)

    def savecfg(self,fileObj):
        new_file = "%s.bak"%self.config_file
        with open(new_file,'wb') as f:
            f.write(fileObj.encode("utf-8"))
            f.close()
        os.remove(self.config_file)
        os.rename(new_file,self.config_file)
        self.statusd['status'] = 'success'
        reload = self.shell("systemctl reload haproxy")
        if reload.wait() == 0:
            self.statusd['info']='文件写入成功，并生效'
            return json.dumps(self.statusd)
        self.statusd['info'] = '文件写入成功，进程未启动'
        return json.dumps(self.statusd)

haproxy = HAFunc()