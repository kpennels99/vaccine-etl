"""Serializer definitions."""
from apps.github_vax import models
from rest_framework import serializers


class GithubVaxDataSerializer(serializers.ModelSerializer):
    """Basic serializer forGithubVaxData model."""

    class Meta:
        """Serialize all fields."""

        model = models.GithubVaxData
        fields = '__all__'
