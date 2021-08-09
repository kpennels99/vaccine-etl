"""Core view definitions."""
from apps.core import serializers
from apps.core.okta_openid.conf import Config
from apps.core.okta_openid.tokens import TokenValidator
from django.contrib.auth import login
from django.http.response import JsonResponse
from okta_oauth2.exceptions import TokenRequestFailed
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView


class OktaLoginView(GenericAPIView):
    """Authenticate user details and generate access and refresh token on success."""

    authentication_classes = []
    permission_classes = []
    serializer_class = serializers.OktaLoginSerializer

    def post(self, request):
        """Authenticate user login."""
        request_data = self.get_serializer(data=request.data)
        serialized_data = request_data.validated_data \
            if request_data.is_valid(raise_exception=True) else None
        config = Config()
        validator = TokenValidator(config, None, request)
        try:
            user, tokens = validator.request_tokens(grant_type='owner_password',
                                                    username=serialized_data['username'],
                                                    password=serialized_data['password'])
        except TokenRequestFailed as login_err:
            raise ValidationError(str(login_err))

        login(request, user)
        return JsonResponse(tokens, status=200)
