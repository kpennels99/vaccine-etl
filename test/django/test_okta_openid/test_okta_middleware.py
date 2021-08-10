"""Okta middleware test cases."""
from http.cookies import SimpleCookie
from okta_oauth2.exceptions import TokenExpired

import pytest
import requests
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework.exceptions import PermissionDenied

from apps.core.okta_openid import middleware
from apps.core.okta_openid.conf import Config
from apps.core.okta_openid.tokens import TokenValidator

UserModel = get_user_model()


def test_get_access_token(mock_http_request, mock_jwt_token):
    """Test whether an access_token is retrieved from request bearer auth header."""
    token = middleware.get_access_token(mock_http_request)
    assert token == mock_jwt_token

def test_validate_or_handle_error_failure(mock_http_request, mock_validate_failure):
    """Test if the correct redirect response is return upon omitting token from cookie."""
    with pytest.raises(PermissionDenied):
        middleware.validate_or_handle_error(Config(), mock_http_request)
    

@pytest.mark.django_db
def test_validate_or_handle_error(mock_http_request, mock_validate_response):
    """Test whether access_token in request's cookie is successfully validated."""
    assert middleware.validate_or_handle_error(Config(), mock_http_request) is None
    mock_validate_response.assert_called_once()


@pytest.mark.parametrize('path', ['/', '/login/'])
def test_okta_middleware(path, mock_validate_or_handle):
    """Test whether OktaMiddleware passes through request upon successful authorization."""
    request = HttpRequest()
    request.path_info = path
    okta_middleware = middleware.OktaMiddleware(lambda x: x)
    assert okta_middleware.config is not None
    response = okta_middleware.__call__(request)
    assert request == response
