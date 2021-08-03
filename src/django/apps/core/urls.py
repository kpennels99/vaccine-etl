"""Social app url configuration."""
from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register('users', viewsets.UserViewSet)

urlpatterns = [
    path('', include(router.urls))
]
