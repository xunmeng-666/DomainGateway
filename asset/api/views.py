# -*- coding:utf-8-*-

from .serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class AssetList(generics.ListCreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
    )


class AssetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    permission_classes = (
        IsAuthenticatedOrReadOnly,
    )


class AssetGroupList(generics.ListCreateAPIView):
    queryset = AssetGroup.objects.all()
    serializer_class = AssetGroupSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
    )


class AssetGroupDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetGroup.objects.all()
    serializer_class = AssetGroupSerializer

    permission_classes = (
        IsAuthenticatedOrReadOnly,
    )

