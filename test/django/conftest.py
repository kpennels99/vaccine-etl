"""Pytest Configuration."""
import os
from textwrap import dedent

import pytest
from django.core.management import call_command
from django.contrib.auth import get_user_model

from okta_oauth2.exceptions import TokenExpired

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('migrate')
        call_command('loaddata', 'github_vax_githubvaxdata.json')


@pytest.fixture
def base_dir():
    """Provide app base directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def logged_in_user(client):
    """Login user on the client object."""
    user = User.objects.create(username='test_user', email='test_user@test.com')
    client.force_login(user)
    return user

@pytest.fixture
def mock_jwt_token():
    """Return well-formed mock JWT."""
    return dedent(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJrZWF0b25AZG90bW9kdXMuY29tIiwibmFt'
        'ZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.Mf6gUBscNHScM15jeTDq3UzlCjFW3tTi4iTywF'
        'nADVQ'
    )


@pytest.fixture
def mock_discovery_document(mocker, monkeypatch):
    """Mock argo client create_namespaced_workflowtemplate method failure."""
    mock_payload = {'token_endpoint': 'https://token_endpoint.com'}
    mocker.patch('apps.core.okta_openid.tokens.DiscoveryDocument.__init__',
                 lambda x, y: None)
    mocker.patch('apps.core.okta_openid.tokens.DiscoveryDocument.get_json',
                 mocker.Mock(return_value=mock_payload))


@pytest.fixture
def mock_token_response(mocker, mock_jwt_token):
    """Mock argo client create_namespaced_workflowtemplate method failure."""
    mock_payload = {'access_token': mock_jwt_token,
                    'refresh_token': 'okta refresh token',
                    'expires_in': 3600,
                    'extra': 'metadata'}
    mock_response = mocker.Mock()
    mock_response.json = mocker.Mock(return_value=mock_payload)
    mock_response.status_code = 200
    mock_post = mocker.patch('requests.post', return_value=mock_response)
    return mock_post


@pytest.fixture
def mock_validate_response(mocker):
    """Mock argo client create_namespaced_workflowtemplate method failure."""
    mock_payload = {'active': True}
    mock_response = mocker.Mock()
    mock_response.json = mocker.Mock(return_value=mock_payload)
    mock_response.status_code = 200
    mock_post = mocker.patch('requests.post', return_value=mock_response)
    return mock_post


@pytest.fixture
def mock_http_request(mocker, mock_jwt_token):
    """Mock http request returned when using Okta login."""
    mock_request = mocker.Mock()
    mock_request.META = {'HTTP_AUTHORIZATION': mock_jwt_token}
    mock_request.method = 'GET'
    return mock_request


@pytest.fixture
def mock_validate_failure(mocker):
    """Mock the Okta middleware validate_token method raising an error."""
    mock_validate = mocker.patch('apps.core.okta_openid.tokens.TokenValidator.validate_access_token', side_effect=[TokenExpired])
    return mock_validate


@pytest.fixture
def mock_validate_or_handle(mocker):
    """Mock Okta middleware validate_tokens method succeeding."""
    mock_validate = mocker.patch('apps.core.okta_openid.middleware.validate_or_handle_error')
    return mock_validate


@pytest.fixture
def mock_authenticate(mocker):
    """Mock Okta TokenValidator tokens_from_auth_code succeeding."""
    mock_user = User.objects.create(username='test', email='test@test.com',
                                    is_active=True)
    mock_authenticate = mocker.patch(
        'apps.core.okta_openid.backend.TokenValidator.tokens_from_auth_code',
        return_value=(mock_user, {'access_token': 'test token'})
    )
    return mock_authenticate


def set_state(state_container, token):
    """Set access_token key of state_container to the token value."""
    mock_user = User.objects.create(username='test', email='test@test.com',
                                    is_active=True)
    state_container.update({'access_token': token})
    return mock_user


@pytest.fixture
def mock_callback_authenticate(mocker, mock_jwt_token):
    """Mock OktaBackend authenticate method succeeding."""
    mock_authenticate = mocker.patch(
        'apps.core.views.okta.authenticate',
        side_effect=lambda request, auth_code, nonce, tokens_store:
        set_state(tokens_store, mock_jwt_token)
    )
    return mock_authenticate
