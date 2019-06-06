# -*- coding:utf-8-*-

from django.conf.urls import url,include
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = format_suffix_patterns([
    url(r'^api-auth/',include('rest_framework.urls')),
    url(r'^asset/',views.AssetList.as_view(),name='asset-list'),
    url(r'^asset/(?P<pk>[0-9]+)/$',views.AssetDetail.as_view(),name='asset-detail'),
    url(r'^asset_group/',views.AssetGroupList.as_view(),name='group-list'),
    url(r'^asset_group/(?P<pk>[0-9]+)/$',views.AssetGroupDetail.as_view(),name='group-detail'),
])