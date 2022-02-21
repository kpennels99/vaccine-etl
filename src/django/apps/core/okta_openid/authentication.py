"""Okta OpenID Authorization Middleware."""
import logging
from typing import Tuple
from typing import Union

from apps.core.okta_openid.conf import Config
from apps.core.okta_openid.tokens import TokenValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from okta_oauth2.exceptions import InvalidToken
from okta_oauth2.exceptions import TokenExpired
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)

UserModel = get_user_model()


class OktaAuthentication(JWTAuthentication):
    """Authenticate user by extracting and validating request bearer Okta token."""

    def authenticate(self, request: HttpRequest) -> Union[None, Tuple[UserModel, str]]:
        """Extract bearer auth header and validate raw token against Okta application.

        Args:
            request (HttpRequest): Incoming HTTP request

        Raises:
            AuthenticationFailed: When request fails TokenExpired, InvalidToken checks.

        Returns:
            Union[None, Tuple[UserModel, str]]: User instance and their Okta access JWT.
        """
        if not settings.USE_OKTA_AUTH:
            return None

        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validator = TokenValidator(Config(), None, request)
        try:
            user, tokens = validator.validate_access_token(raw_token)
        except (TokenExpired, InvalidToken) as okta_auth_error:
            raise exceptions.AuthenticationFailed(str(okta_auth_error))

        return user, str(tokens['access_token'])
