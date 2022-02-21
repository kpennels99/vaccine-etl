"""Github Vax data app url configuration."""
from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register(r'vax_data', viewsets.GithubVaxDataViewSet)
router.register(r'graph_report', viewsets.GraphReportViewSet)

urlpatterns = [
    path('', include(router.urls))
]
