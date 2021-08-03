from django.contrib.auth.hashers import make_password
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
            raise serializers.ValidationError("Password cannot be empty.")
        return make_password(value)

    def validate_email(self, value: str) -> str:
        """Ensure email field is not empty."""
        if value == '':
            raise serializers.ValidationError("Email cannot be empty.")
        return value
