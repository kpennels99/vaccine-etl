"""Viewset definitions."""
from rest_framework import viewsets

from . import filtersets
from . import models
from . import serializers

class GithubVaxDataViewSet(viewsets.ReadOnlyModelViewSet):
    """PetFeature CRUD operations."""

    queryset = models.GithubVaxData.objects.all().order_by('-date')
    serializer_class = serializers.GithubVaxDataSerializer
    filterset_class = filtersets.GithubVaxDataFilter

    # TODO: add actions to 1) lastest data 2) average daily vaccinations
