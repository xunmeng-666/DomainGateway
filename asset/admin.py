from django.contrib import admin

# Register your models here.
from .admin_base import site,BaseAdmin
from . import models

class AssetAdmin(BaseAdmin):
    list_display = ("id","name","http","domain","sport","ip",'dport','ssl',"group",'remarks')
    list_filter = ["ID","名称","HTTP协议","域名","HA开放端口","后端服务器",'远端服务端口','证书路径',"组","备注"]
    export_fields = list_display
    list_per_page = 15
    search_fields = ['name','domain','ip']

class AssetGroupAdmin(BaseAdmin):
    list_display = ("id","name",'asset',"remarks")
    list_filter = ["ID","组名","网站数量","备注"]
    list_per_page = 10
    search_fields = ['name']

class AssetCheckAdmin(BaseAdmin):
    list_display = ("id","asset_id",'status_code')

class LogsAdmin(BaseAdmin):
    list_display = ('date', "user", 'action','content')
    list_filter = ['日期', '用户', '行为','内容']
    list_per_page = 20

site.register(models.Asset,AssetAdmin)
site.register(models.AssetGroup,AssetGroupAdmin)
site.register(models.Logs,LogsAdmin)
site.register(models.AssetCheck,AssetCheckAdmin)
admin.site.register(models.Asset)
admin.site.register(models.AssetGroup)