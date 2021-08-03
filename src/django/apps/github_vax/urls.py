"""Social app url configuration."""
from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register(r'vax_data', viewsets.GithubVaxDataViewSet, basename='vax_data')

urlpatterns = [
    path('', include((router.urls, 'github_vax'), 'api'), name='api-root')
]
