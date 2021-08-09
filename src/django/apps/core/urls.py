"""Social app url configuration."""
from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from apps.core import viewsets
from apps.core.views import OktaLoginView

router = routers.DefaultRouter()
router.register('users', viewsets.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('okta_login', OktaLoginView.as_view(), name="okta_login")
]
