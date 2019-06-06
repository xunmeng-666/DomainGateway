from django.db import models
from .core.haproxy import haproxy
from django.contrib.postgres.fields import JSONField

# Create your models here.

class Asset(models.Model):
    http_choice=(
        (0,'http'),
        (1,'https'),
    )
    name = models.CharField(verbose_name='名称',max_length=32,blank=True,null=True,unique=True)
    http = models.SmallIntegerField(verbose_name='HTTP协议',choices=http_choice,default=0)
    domain = models.CharField(verbose_name='域名',max_length=32,unique=True)
    sport = models.IntegerField(verbose_name='HA开放端口',)
    ip = models.GenericIPAddressField(verbose_name='远端服务器IP',)
    dport = models.IntegerField(verbose_name='远端服务端口',)
    ssl = models.CharField(verbose_name='证书路径',max_length=32,blank=True,null=True)
    remarks = models.CharField(verbose_name='备注',max_length=32,blank=True,null=True)

    class Meta:
        verbose_name = '网站'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.name

class AssetGroup(models.Model):
    name = models.CharField(verbose_name='组',max_length=32,unique=True)
    asset = models.ManyToManyField(Asset,verbose_name='网站列表',related_name='assetgroup',blank=True,null=True)
    remarks = models.CharField(verbose_name='备注',max_length=32,blank=True,null=True)

    class Meta:
        verbose_name = '组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" %self.name

class AssetCheck(models.Model):
    asset = models.ForeignKey(Asset)
    status_code = models.IntegerField(blank=True,null=True)

    class Meta:
        verbose_name = '状态'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" %self.status_code

class Logs(models.Model):
    user = models.CharField(max_length=32)
    action = models.CharField(max_length=32,)
    content = JSONField()
    date = models.DateTimeField(auto_now_add=False)

    class Meta:
        verbose_name = '日志'
        verbose_name_plural = verbose_name

