"""Okta OpenID view tests."""
from http.cookies import SimpleCookie

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def mock_call_endpoint(mocker, mock_jwt_token):
    mock_payload = {
        "access_token": mock_jwt_token,
        "refresh_token": "refresh",
        "expires_in": 3600
    }
    mocker.patch('apps.core.views.TokenValidator.call_token_endpoint',
                 mocker.Mock(return_value=mock_payload))

@pytest.mark.django_db
def test_login(client, mock_call_endpoint):
    """Test whether a user is logged in when valid credentials are provided."""
    user = User.objects.filter(username="keaton@dotmodus.com")
    assert not user.exists()
    resp = client.post(reverse('core:okta_login'),
                       data={"username": "keaton@dotmodus.com",
                             "password": "password123"})
    assert resp.status_code == 200
    assert user.exists()
    user = user[0]
    assert user.is_authenticated
