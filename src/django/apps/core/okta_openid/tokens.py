"""Okta OpenID Oauth2 JWT validator."""
import base64
import logging
from typing import Any
from typing import Dict
from typing import Tuple

import jwt
import requests
from apps.core.okta_openid.conf import Config
from django.contrib.auth import get_user_model
from django.http.request import HttpRequest
from okta_oauth2.exceptions import InvalidToken
from okta_oauth2.exceptions import TokenExpired
from okta_oauth2.exceptions import TokenRequestFailed

logger = logging.getLogger(__name__)

UserModel = get_user_model()


class DiscoveryDocument:
    """OpenID authorization server metadata adapter."""

    def __init__(self, issuer_uri: str):
        """Request metadata information for the configured issuer_uri.

        Args:
            issuer_uri (str): Public Okta URL describing the application server endpoints.
        """
        r = requests.get(f'{issuer_uri}/.well-known/openid-configuration')
        self.json = r.json()

    def get_json(self) -> dict:
        """Return Okta application configuration.

        Returns:
            dict: Okta application dict describing available authn/authz endpoints.
        """
        return self.json


class TokenValidator:
    """Generate and remotely validate Okta OpenID JWTs."""

    _discovery_document = None

    def __init__(self, config: Config, nonce: str, request: HttpRequest):
        """Initialise instance attributes.

        Args:
            config (Config): Okta config adapter class.
            nonce (str): Okta returned security nonce.
            request (HttpRequest): Incoming HTTP request.
        """
        self.config = config
        self.request = request
        self.nonce = nonce
        self.token_endpoint = self.discovery_document.get_json()['token_endpoint']

    @property
    def discovery_document(self) -> DiscoveryDocument:
        """Return discovery document singleton.

        Returns:
            DiscoveryDocument: Class wrapping access to Okta application server endpoints.
        """
        if self._discovery_document is None:
            self._discovery_document = DiscoveryDocument(self.config.issuer)

        return self._discovery_document

    def get_owner_password_data(self, username: str, password: str) -> Dict[str, Any]:
        """Return data required to make resource owner password token request.

        Args:
            username (str): Okta username.
            password (str): Okta password.

        Returns:
            Dict[str, Any]: Okta request post data required for resource owner grant.
        """
        return {'grant_type': 'password', 'scope': self.config.scopes,
                'username': username, 'password': password}

    def get_auth_code_data(self, code: str) -> Dict[str, Any]:
        """Return data required to make authorization code token request.

        Args:
            code (str): Okta authorization code returned from OAuth login request.

        Returns:
            Dict[str, Any]: Okta request post data required for authorization code grant.
        """
        return {'grant_type': 'authorization_code', 'code': str(code),
                'scope': self.config.scopes}

    def get_refresh_data(self, refresh_token: str) -> Dict[str, Any]:
        """Return data required to make refresh access token request.

        Args:
            refresh_token (str): Okta JWT refresh token.

        Returns:
            Dict[str, Any]: Okta request post data required for refresh token grant.
        """
        return {'grant_type': 'refresh_token', 'refresh_token': str(refresh_token),
                'scope': self.config.scopes, 'redirect_uri': self.config.redirect_uri}

    def request_tokens(self, grant_type: str = 'owner_password',
                       *args, **kwargs) -> Tuple[UserModel, Dict[str, Any]]:
        """Call the token endpoint using the payload for the respective grant type.

        Args:
            grant_type (str, optional): Name of grant type to request from Okta. Defaults
                to 'owner_password'.

        Raises:
            Exception: When TokenValidator class does not contain grant_type as an attr.

        Returns:
            Tuple[UserModel, Dict[str, Any]]: Corresponding user and their JWT tokens from
                the grant type request.
        """
        grant_type_data_function = f'get_{grant_type}_data'
        if not hasattr(self, grant_type_data_function):
            raise AttributeError('Not configured to request tokens using the '
                                 f'grant_type: {grant_type}')

        data = getattr(self, grant_type_data_function)(*args, **kwargs)
        token_result = self.call_token_endpoint(self.token_endpoint, data)
        return self.handle_token_result(token_result)

    def call_token_endpoint(self, url: str,
                            endpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make request authorization server's /token endpoint.

        Args:
            url (str): Okta authentication/authorization endpoint
            endpoint_data (Dict[str, Any]): POST data related to Okta endpoint.

        Raises:
            TokenRequestFailed: Non successful status code returned from Okta.

        Returns:
            Dict[str, Any]: Dict version of JSON response returned from Okta.
        """
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

    def handle_token_result(
            self,
            token_result: Dict[str, Any]
            ) -> Tuple[UserModel, Dict[str, Any]]:
        """Get or create user and extract the required Okta token related values.

        Args:
            token_result (Dict[str, Any]): JWT token payload returned from Okta.

        Raises:
            InvalidToken: When the access_token is not able to be decoded.

        Returns:
            Tuple[UserModel, Dict[str, Any]]: Corresponding user and their JWT tokens from
            the grant type request.
        """
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

    def validate_access_token(self, token: str) -> Tuple[UserModel, Dict[str, Any]]:
        """Remotely validate whether access token is still active / not expired.

        Args:
            token (str): Okta JWT token

        Raises:
            TokenExpired: If Okta registers the supplied token as invalid.

        Returns:
            Tuple[UserModel, Dict[str, Any]]: Corresponding user and their JWT tokens from
                the va;idate request.
        """
        validate_response = self.call_token_endpoint(
            f'{self.config.issuer}/v1/introspect',
            {'token': token, 'token_type_hint': 'access_token'}
        )
        if not validate_response['active']:
            raise TokenExpired('Token expired')

        return self.handle_token_result({'access_token': token})
