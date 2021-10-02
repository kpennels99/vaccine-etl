"""Okta django permissions."""
import jwt
from django.conf import settings
from rest_framework import permissions


class OktaHasGraphingAccess(permissions.IsAuthenticated):
    """Okta OpenID connect claim validator."""

    def has_permission(self, request, view):
        """Validate whether user's Okta token contains a true has_graphing_access claim."""
        if not settings.USE_OKTA_AUTH:
            return super().has_permission(request, view)

        auth_header = request.META['HTTP_AUTHORIZATION']
        access_token = auth_header.strip().split(' ')[-1]
        claims = jwt.decode(access_token, verify=False)
        return claims.get('has_graphing_access', False)
