# -*- coding:utf-8-*-

from asset.models import *
from rest_framework import serializers
from ..core.haproxy import haproxy

class AssetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Asset
        fields = ("url","name","http","domain","sport","ip","dport","ssl","remarks")

    def save(self, **kwargs):
        if self.validated_data['ssl']:
            self.validated_data['ssl'] = haproxy.savessl(self.validated_data['ssl'])
        super(self.__class__,self).save(**kwargs)
        haproxy.buildcfg(Asset.objects)


class AssetGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssetGroup
        fields = "__all__"
