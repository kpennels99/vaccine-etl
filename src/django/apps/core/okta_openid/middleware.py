"""Okta OpenID Authorization Middleware."""
import logging

from apps.core.okta_openid.conf import Config
from apps.core.okta_openid.tokens import TokenValidator
from django.http import HttpRequest
from okta_oauth2.exceptions import InvalidToken
from okta_oauth2.exceptions import TokenExpired
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


def get_access_token(request: HttpRequest):
    """Extract Okta access token if present in request."""
    auth_header = request.META.get('HTTP_AUTHORIZATION').strip()
    if not auth_header:
        raise PermissionDenied('Okta access token not present in request.')

    return auth_header.split(' ')[-1]


def validate_or_handle_error(config: Config, request: HttpRequest):
    """Ensure request contains valid Okta tokens else respond with error."""
    access_token = get_access_token(request)
    validator = TokenValidator(config, None, request)
    try:
        validator.validate_access_token(access_token)
    except (TokenExpired, InvalidToken) as okta_auth_error:
        raise PermissionDenied(str(okta_auth_error))


class OktaMiddleware:
    """Validate OpenID OAuth2 Okta access JWT."""

    def __init__(self, get_response):
        """Initialise instance variables."""
        self.config = Config()
        self.get_response = get_response

    def __call__(self, request):
        """Extract Okta JWT and remotely validate it against the apps auth server."""
        logger.debug(f'entering okta middleware for {request.path_info}')
        if self.is_public_url(request.path_info):
            logger.debug('Public url encountered. Skipping token validation')
            return self.get_response(request)

        try:
            validate_or_handle_error(self.config, request)
        except PermissionDenied as auth_error:
            logger.error(f'{request.path_info}: Failed Okta token validation for user '
                         f"{getattr(request, 'user')}")

            raise auth_error

        return self.get_response(request)

    def is_public_url(self, url):
        """Check whether url matches any of the configured publicly accessible patterns."""
        return any(public_url.match(url) for public_url in self.config.public_urls)
