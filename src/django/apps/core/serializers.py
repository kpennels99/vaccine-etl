from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    """Basic serializer for User model."""

    class Meta:
        """Serialize all fields and exclude password from being read."""

        model = models.User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value: str) -> str:
        """Ensure password field is not empty."""
        if value == '':
            raise serializers.ValidationError('Password cannot be empty.')

        validate_password(value)
        return make_password(value)

    def validate_email(self, value: str) -> str:
        """Ensure email field is not empty."""
        if value == '':
            raise serializers.ValidationError('Email cannot be empty.')
        return value

class OktaLoginSerializer(serializers.Serializer):
    """Serialize Okta login POST request."""

    username = serializers.CharField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)
