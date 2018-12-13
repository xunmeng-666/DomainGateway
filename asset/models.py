from django.db import models

# Create your models here.

class Asset(models.Model):
    name = models.CharField(verbose_name='名称',max_length=32,unique=True)
    domain = models.CharField(verbose_name='域名',max_length=32,unique=True)
    ip = models.GenericIPAddressField(verbose_name='IP地址',unique=True)
    group = models.ForeignKey('AssetGroup',blank=True,null=True)
    remarks = models.CharField(verbose_name='备注',max_length=32,blank=True,null=True)

    class Meta:
        verbose_name = '网站'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" % self.name

class AssetGroup(models.Model):
    name = models.CharField(verbose_name='组',max_length=32,unique=True)
    remarks = models.CharField(verbose_name='备注',max_length=32,blank=True,null=True)

    class Meta:
        verbose_name = '组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s" %self.name