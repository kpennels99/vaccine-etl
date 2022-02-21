"""Okta Auth Configuration Adapter."""
import re
from typing import List

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch
from django.urls import reverse

# We can't check for tokens on these URL's
# because we won't have them.
DEFAULT_PUBLIC_NAMED_URLS = (
    'accounts_login',
    'accounts_logout',
    'accounts_callback',
    'okta_login',
)


class Config:
    """Okta Auth configuration adapter class."""

    def __init__(self):
        """Initialise instance variables with configured OKTA_AUTH Django settings.

        Raises:
            ImproperlyConfigured: When expected Django setting is not accessible.
        """
        try:
            # Configuration object
            self.org_url = settings.OKTA_AUTH['ORG_URL']

            # OpenID Specific
            self.client_id = settings.OKTA_AUTH['CLIENT_ID']
            self.client_secret = settings.OKTA_AUTH['CLIENT_SECRET']
            self.issuer = settings.OKTA_AUTH['ISSUER']
            self.scopes = settings.OKTA_AUTH.get(
                'SCOPES', 'openid profile email offline_access'
            )
            self.redirect_uri = settings.OKTA_AUTH['REDIRECT_URI']
            self.login_redirect_url = settings.OKTA_AUTH.get('LOGIN_REDIRECT_URL', '/')

            # Django Specific
            self.idp_embed_link = settings.OKTA_AUTH.get('IDP_EMBED_LINK')
            self.public_urls = self.build_public_urls()
        except (AttributeError, KeyError):
            raise ImproperlyConfigured('Missing Okta authentication settings')

    def build_public_urls(self) -> List[str]:
        """Build combined list of reversed PUBLIC_NAMED_URLS as well as PUBLIC_URLS.

        Returns:
            List[str]: List of regex compiled urls not requiring Okta authentication.
        """
        public_named_urls = (
            settings.OKTA_AUTH.get('PUBLIC_NAMED_URLS', ()) + DEFAULT_PUBLIC_NAMED_URLS
        )

        named_urls = []
        for name in public_named_urls:
            try:
                named_urls.append(reverse(name))
            except NoReverseMatch:
                pass

        public_urls = tuple(settings.OKTA_AUTH.get('PUBLIC_URLS', ())) + tuple(
            ['^%s$' % url for url in named_urls]
        )

        return [re.compile(u) for u in public_urls]
