"""TokenValidator test cases."""
import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from apps.core.okta_openid.conf import Config
from apps.core.okta_openid.tokens import TokenValidator

UserModel = get_user_model()


def test_discovery_document(mock_discovery_document):
    """Test whether discovery_document property get initialized as a Singleton."""
    assert TokenValidator._discovery_document is None
    validator = TokenValidator(Config(), None, HttpRequest())
    document = validator.discovery_document.get_json()
    assert validator._discovery_document is not None
    assert 'token_endpoint' in document


def test_call_token_endpoint(mock_discovery_document, mock_token_response):
    """Test whether the Okta token endpoint returns the expected key value pairs."""
    validator = TokenValidator(Config(), None, HttpRequest())
    token_result = validator.call_token_endpoint('https://okta.com/v1/token/',
                                                 {'data': 'mock endpoint data'})
    assert isinstance(token_result, dict)
    assert token_result['access_token'] == 'okta access token'
    assert token_result['refresh_token'] == 'okta refresh token'
    assert token_result['expires_in'] == 3600


@pytest.mark.django_db
def test_validate_access_token(mock_validate_response, mock_jwt_token):
    """Test whether a valid access token is validated as expected."""
    validator = TokenValidator(Config(), None, HttpRequest())
    assert validator.validate_access_token(mock_jwt_token) is None
    mock_validate_response.assert_called_once()


@pytest.mark.django_db
def test_handle_token_result(mock_http_request, mock_validate_response,
                             mock_jwt_token):
    """Test whether a user is created from the claims contained in a valid access token."""
    validator = TokenValidator(Config(), None, mock_http_request)
    assert len(UserModel.objects.filter(email='keaton@dotmodus.com')) == 0
    token_result = {'access_token': mock_jwt_token, 'refresh_token': 'refresh'}
    validator.handle_token_result(token_result)
    assert len(UserModel.objects.filter(email='keaton@dotmodus.com')) == 1
    assert 'extra' not in token_result