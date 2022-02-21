"""Okta authentication test cases."""
from http.cookies import SimpleCookie
from okta_oauth2.exceptions import TokenExpired

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from apps.core.okta_openid.authentication import OktaAuthentication
from apps.core.okta_openid.permissions import OktaHasGraphingAccess

UserModel = get_user_model()



@pytest.mark.django_db
def test_okta_authentication(mock_jwt_token, settings, mock_validate_response):
    settings.USE_OKTA_AUTH = True
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = f"Bearer {mock_jwt_token}"
    okta_django_auth = OktaAuthentication()
    result = okta_django_auth.authenticate(request)
    assert len(result) == 2
    mock_validate_response.assert_called_once()
    user, _ = result
    assert user.email == "keaton@dotmodus.com"


@pytest.mark.django_db
def test_okta_authentication(mock_jwt_token, settings):
    settings.USE_OKTA_AUTH = True
    request = HttpRequest()
    request.META["HTTP_AUTHORIZATION"] = f"Bearer {mock_jwt_token}"
    okta_django_perm = OktaHasGraphingAccess()
    assert okta_django_perm.has_permission(request, None) == False
    