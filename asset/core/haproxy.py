# -*- coding:utf-8-*-
import subprocess
import json
import os
import requests
from django.utils.datastructures import MultiValueDictKeyError
from checkurl import Object


class HaproxyFunc(object):
    def __init__(self):
        self.name = None
        self.domain = None
        self.sport = None
        self.ip = None
        self.dport = None
        self.crt = None
        self.config_file = '/etc/haproxy/haproxy.cfg'
        self.sslfile_path = '/etc/haproxy/ssl/'
        self.statusd = {"status": '', 'info': ''}
        self.session = requests.session()

    def variable(self,request):
        # 解析request.POST中的value
        self.name = request.POST['name']
        self.domain = request.POST['domain']
        self.sport = request.POST['sport']
        self.ip = request.POST['ip']
        self.dport = request.POST['dport']
        try:
            if request.POST['ssl']:
                self.crt = request.POST['ssl']
                self.write(self.https_cfg(),self.config_file)
            else:
                self.write(self.http_cfg(),self.config_file)
        except MultiValueDictKeyError :
            self.write(self.http_cfg(),self.config_file)
        self.shell('systemctl restart haproxy')
        self.checkGFW()

    def _sslpath(self):
        if os.path.exists(self.sslfile_path):
            return True
        os.mkdir(self.sslfile_path)
        return True

    def savessl(self,file):
        self._sslpath()
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
        self.shell("echo '%s' > %s" %(cfg,file))
        os.system("cat %s" % file)
        return True

    def write_cfg(self,cfg,file):
        self.shell("echo '%s' >> %s" %(cfg,file))
        os.system("cat %s" %file)
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

    def save_cfg(self,new_file,old_file):
        if os.path.exists(old_file):
            os.remove(old_file)
        os.rename(new_file,old_file)
        return True

    def buildcfg(self,admin_class):
        new_file = "%s.bak" %self.config_file
        info = admin_class.model.objects.values()
        self.write(cfg=self.defalut_func(),file=new_file)
        try:
            for obj in info:
                self.name = obj['name']
                self.sport = obj['sport']
                self.ip = obj['ip']
                self.dport = obj['dport']
                self.domain = obj['domain']
                self.crt = obj['ssl']
                self.http = obj['http']
                if obj['ssl'] is not None:
                    self.write_cfg(self.https_cfg(),new_file)
                else:
                    self.write_cfg(self.http_cfg(),new_file)

            try:
                os.remove(self.config_file)
            except FileNotFoundError:
                pass
            os.rename(new_file,self.config_file)

            cmd = self.shell("systemctl reload haproxy")
            return info
        except KeyError as e:
            pass

    def join_url(self,info):
        _url = {'host':[]}
        for field in info:
            http = 'http'
            host = field['ip']
            port = field['dport']
            domain = field['domain']
            verify = field.get("ssl")
            url = "%s://%s:%s" %(http,host,port)
            _url['host'].append({'id':field['id'],'http':http,'host':host,'port':port,'domain':domain,'verify':verify,'url':url})
        return _url
    def checkc_url(self,_url):
        for url in _url['host']:
            try:
                status_code = requests.get(url['url'],verify=False).status_code
                url['status_code'] = status_code
            except requests.ConnectionError:
                status_code = 504
                url['status_code'] = status_code
        return _url
    def save_code(self,admin_class,url):
        assetcheck = admin_class.model.assetcheck_set.field.model
        for code in url['host']:
            if assetcheck.objects.filter(asset_id=code['id']):
                as_id = assetcheck.objects.filter(asset_id=code['id']).values('id')[0]['id']
                assetcheck.objects.filter(id=as_id).update(asset_id=int(code['id']),status_code=int(code['status_code']))
            else:
                assetcheck.objects.create(asset_id=int(code['id']),status_code=int(code['status_code']))

    def run(self,admin_class):
        self.buildcfg(admin_class)

    def get_code(self,admin_class):
        info = admin_class.model.objects.values()
        _url = self.join_url(info)
        url = self.checkc_url(_url)
        self.save_code(admin_class, url)

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