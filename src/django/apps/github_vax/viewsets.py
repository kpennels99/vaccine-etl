"""Viewset definitions."""
from apps.github_vax import filtersets
from apps.github_vax import models
from apps.github_vax import serializers
from rest_framework import viewsets


class GithubVaxDataViewSet(viewsets.ReadOnlyModelViewSet):
    """PetFeature CRUD operations."""

    queryset = models.GithubVaxData.objects.all().order_by('-date')
    serializer_class = serializers.GithubVaxDataSerializer
    filterset_class = filtersets.GithubVaxDataFilter

    # TODO: add actions to 1) lastest data 2) average daily vaccinations
