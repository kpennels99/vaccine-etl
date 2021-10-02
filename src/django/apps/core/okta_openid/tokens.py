"""Okta OpenID Oauth2 JWT validator."""
import base64
import logging

import jwt
import requests
from django.contrib.auth import get_user_model
from okta_oauth2.exceptions import InvalidToken
from okta_oauth2.exceptions import TokenExpired
from okta_oauth2.exceptions import TokenRequestFailed

logger = logging.getLogger(__name__)

UserModel = get_user_model()


class DiscoveryDocument:
    """OpenID authorization server metadata adapter."""

    def __init__(self, issuer_uri):
        """Request metadata information for the configured issuer_uri."""
        r = requests.get(issuer_uri + '/.well-known/openid-configuration')
        self.json = r.json()

    def get_json(self):
        """Return json attribute."""
        return self.json


class TokenValidator:
    """Generate and remotely validate Okta OpenID JWTs."""

    _discovery_document = None

    def __init__(self, config, nonce, request):
        """Initialise instance attributes."""
        self.config = config
        self.request = request
        self.nonce = nonce
        self.token_endpoint = self.discovery_document.get_json()['token_endpoint']

    @property
    def discovery_document(self):
        """Return discovery document singleton."""
        if self._discovery_document is None:
            self._discovery_document = DiscoveryDocument(self.config.issuer)

        return self._discovery_document

    def get_owner_password_data(self, username, password):
        """Return data required to make resource owner password token request."""
        return {'grant_type': 'password', 'scope': self.config.scopes,
                'username': username, 'password': password}

    def get_auth_code_data(self, code):
        """Return data required to make authorization code token request."""
        return {'grant_type': 'authorization_code', 'code': str(code),
                'scope': self.config.scopes}

    def get_refresh_data(self, refresh_token):
        """Return data required to make refresh access token request."""
        return {'grant_type': 'refresh_token', 'refresh_token': str(refresh_token),
                'scope': self.config.scopes, 'redirect_uri': self.config.redirect_uri}

    def request_tokens(self, grant_type='owner_password', *args, **kwargs):
        """Call the token endpoint using the payload for the respective grant type."""
        grant_type_data_function = f'get_{grant_type}_data'
        if not hasattr(self, grant_type_data_function):
            raise Exception('Not configured to request tokens using the grant_type'
                            f'{grant_type}')

        data = getattr(self, grant_type_data_function)(*args, **kwargs)
        token_result = self.call_token_endpoint(self.token_endpoint, data)
        return self.handle_token_result(token_result)

    def call_token_endpoint(self, url, endpoint_data):
        """Make request authorization server's /token endpoint."""
        basic_auth_value = base64.b64encode(
            f'{self.config.client_id}:{self.config.client_secret}'.encode()
        )
        r = requests.post(
            url=url,
            headers={
                'Authorization': 'Basic: ' + basic_auth_value.decode('utf-8'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            params=endpoint_data
        )

        response = r.json()
        if not 200 <= r.status_code <= 299:
            raise TokenRequestFailed(response.get('error') or response.get('errorCode'))

        return response

    def handle_token_result(self, token_result):
        """Get or create user and extract the required Okta token related values."""
        if token_result is None or 'access_token' not in token_result:
            return None, {}

        try:
            claims = jwt.decode(token_result['access_token'], verify=False)
        except jwt.exceptions.DecodeError:
            raise InvalidToken('Unable to decode jwt')
        try:
            user = UserModel._default_manager.get_by_natural_key(claims['sub'])
        except UserModel.DoesNotExist:
            user = UserModel._default_manager.create_user(
                username=claims['sub'], email=claims['sub'], is_active=True
            )

        tokens = {expected_key: token_result[expected_key]
                  for expected_key in ['access_token', 'refresh_token', 'expires_in']
                  if expected_key in token_result}

        return user, tokens

    def validate_access_token(self, token):
        """Remotely validate whether access token is still active / not expired."""
        validate_response = self.call_token_endpoint(
            f'{self.config.issuer}/v1/introspect',
            {'token': token, 'token_type_hint': 'access_token'}
        )
        if not validate_response['active']:
            raise TokenExpired('Token expired')

        return self.handle_token_result({'access_token': token})
