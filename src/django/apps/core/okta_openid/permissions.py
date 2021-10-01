import jwt
from rest_framework import permissions
from django.conf import settings


class OktaHasGraphingAccess(permissions.IsAuthenticated):
    
    def has_permission(self, request, view):
        if not settings.USE_OKTA_AUTH:
            return super().has_permission(request, view)
        
        auth_header = request.META['HTTP_AUTHORIZATION']
        access_token = auth_header.strip().split(' ')[-1]
        claims = jwt.decode(access_token, verify=False)
        print(claims)
        if claims.get('has_graphing_access'):
            return True