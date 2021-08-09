"""Okta OpenID Authentication Backend."""
from apps.core.okta_openid.conf import Config
from apps.core.okta_openid.tokens import TokenValidator
from django.contrib.auth.backends import ModelBackend


class OktaAuthCodeBackend(ModelBackend):
    """Authentication using Okta's OIDC authorization servers.

    The Okta sign in widget will accept a username and password,
    validate them, and if successful return an authorization code.

    We take that code and use it to obtain an Access Token and a Refresh Token from Okta,
    and create or get the user from the Django database.
    """

    def authenticate(self, request, auth_code=None, nonce=None, tokens_store=None):
        """Authenticate request and generate Okta OpenID access and refresh JWTs."""
        if auth_code is None or nonce is None or tokens_store is None:
            return

        validator = TokenValidator(Config(), nonce, request)
        user, tokens = validator.tokens_from_auth_code(auth_code)
        tokens_store.update(tokens)

        if self.user_can_authenticate(user):
            return user

class OktaCredentialsBackend(ModelBackend):
    """Authentication using Okta's OIDC authorization servers.

    The Okta sign in widget will accept a username and password,
    validate them, and if successful return an authorization code.

    We take that code and use it to obtain an Access Token and a Refresh Token from Okta,
    and create or get the user from the Django database.
    """

    def authenticate(self, request, auth_code=None, nonce=None, tokens_store=None):
        """Authenticate request and generate Okta OpenID access and refresh JWTs."""
        if auth_code is None or nonce is None or tokens_store is None:
            return

        validator = TokenValidator(Config(), nonce, request)
        user, tokens = validator.tokens_from_auth_code(auth_code)
        tokens_store.update(tokens)

        if self.user_can_authenticate(user):
            return user
