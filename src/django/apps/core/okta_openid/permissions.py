"""Okta django permissions."""
import jwt
from django.conf import settings
from django.http.request import HttpRequest
from rest_framework import permissions


class OktaHasGraphingAccess(permissions.IsAuthenticated):
    """Okta OpenID connect claim validator."""

    def has_permission(self, request: HttpRequest, view) -> bool:
        """Validate whether user's Okta token contains a true has_graphing_access claim.

        Args:
            request (HttpRequest): Incoming HTTP request.
            view: View setup to handle incoming HTTP request.

        Returns:
            bool: Whether request is authorized to acccess the view
        """
        if not settings.USE_OKTA_AUTH:
            return super().has_permission(request, view)

        auth_header = request.META['HTTP_AUTHORIZATION']
        access_token = auth_header.strip().split(' ')[-1]
        claims = jwt.decode(access_token, verify=False)
        return claims.get('has_graphing_access', False)
