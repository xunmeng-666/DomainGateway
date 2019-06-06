"""gateway URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from asset import views


urlpatterns = [
    url(r'^(\w+)/list/$', views.table_obj_list),
    url(r'^(\w+)/add/$', views.table_obj_add),
    url(r'^(\w+)/change/$', views.table_obj_change),
    url(r'^(\w+)/del/$', views.table_obj_del),
    url(r'^(\w+)/haproxy/$', views.haproxyd),
    url(r'^haproxy/list/$', views.ha_cfg_list,name='ha_list'),
    url(r'^haproxy/save/$', views.ha_cfg_save,name='ha_save'),
    url(r'^haproxy/command/$', views.ha_command,name='ha_command'),
    url(r'^haproxy/content/$', views.ha_content,name='ha_content'),
    url(r'^haproxy/status_info/$', views.ha_status,name='ha_status'),
    url(r'^haproxy/save_cfg/$', views.save_cfg,name='save_cfg'),
    url(r'^haproxy/restart/$', views.restart,name='restart'),
    url(r'^logs/$', views.logs),
]
