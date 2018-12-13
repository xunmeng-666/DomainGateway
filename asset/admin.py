from django.contrib import admin

# Register your models here.
from .admin_base import site,BaseAdmin
from . import models

class AssetAdmin(BaseAdmin):
    list_display = ("id","name","domain","ip","group",'remarks')
    list_filter = ["ID","名称","域名","IP地址","组","备注"]
    export_fields = list_display
    list_per_page = 10
    search_fields = ['name','domain','ip']

class AssetGroupAdmin(BaseAdmin):
    list_display = ("id","name","remarks")
    list_filter = ["ID","组名","备注"]
    list_per_page = 10
    search_fields = ['name']


site.register(models.Asset,AssetAdmin)
site.register(models.AssetGroup,AssetGroupAdmin)

admin.site.register(models.Asset)
admin.site.register(models.AssetGroup)