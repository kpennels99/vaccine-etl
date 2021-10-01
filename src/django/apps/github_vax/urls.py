"""Github Vax data app url configuration."""
from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register(r'vax_data', viewsets.GithubVaxDataViewSet, basename='vax_data')
router.register(r'graph_report', viewsets.GraphReportViewSet, basename='graph_report')

urlpatterns = [
    path('', include((router.urls, 'github_vax'), 'api'), name='api-root')
]
