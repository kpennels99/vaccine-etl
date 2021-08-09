"""Okta OpenID Authorization Middleware."""
import logging

from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.urls import reverse
from okta_oauth2.exceptions import InvalidToken
from okta_oauth2.exceptions import MissingAuthTokens
from okta_oauth2.exceptions import TokenExpired

from apps.core.okta_openid.conf import Config
from apps.core.okta_openid.tokens import TokenValidator

logger = logging.getLogger(__name__)


def get_access_token(request: HttpRequest):
    """Extract Okta access token if present in request."""
    token = request.COOKIES.get('tokens')
    if not token:
        raise MissingAuthTokens('Okta access token not present in request.')

    return token


def validate_tokens(config: Config, request: HttpRequest):
    """Ensure Okta access token has not expired by remotely validating it."""
    access_token = get_access_token(request)
    try:
        nonce = request.COOKIES['okta-oauth-nonce']
    except KeyError:
        # If we don't have a nonce set on authentication by the client
        # in the cookie then we can't validate the token, so just raise an invalid token
        raise InvalidToken('Missing nonce in cookie')

    validator = TokenValidator(config, nonce, request)
    validator.validate_access_token(access_token)


def validate_or_handle_error(config: Config, request: HttpRequest):
    """Ensure request contains valid Okta tokens else respond with error/redirect."""
    try:
        validate_tokens(config, request)
    except MissingAuthTokens:
        if request.method == 'POST':
            # Posting shouldn't redirect, it should just say no.
            return JsonResponse({'error': 'Token has expired'}, status=403)

        return HttpResponseRedirect(reverse('login'))
    except (TokenExpired, InvalidToken):
        return HttpResponseRedirect(reverse('login'))


class OktaMiddleware:
    """Validate OpenID OAuth2 Okta access JWT."""

    def __init__(self, get_response):
        """Initialise instance variables."""
        self.config = Config()
        self.get_response = get_response

    def __call__(self, request):
        """Extract Okta JWT and remotely validate it against the apps auth server."""
        print(f'entering okta middleware for {request.path_info}')
        if self.is_public_url(request.path_info):
            print(f'public url')
            return self.get_response(request)

        error_response = validate_or_handle_error(self.config, request)
        if error_response:
            logger.error(f'{request.path_info}: Failed Okta token validation for user '
                         f"{getattr(request, 'user')}")

            return error_response

        return self.get_response(request)

    def is_public_url(self, url):
        """Check whether url matches any of the configured publicly accessible patterns."""
        return any(public_url.match(url) for public_url in self.config.public_urls)
