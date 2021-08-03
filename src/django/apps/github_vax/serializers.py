from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.github_vax import models

class GithubVaxDataSerializer(serializers.ModelSerializer):
    """Basic serializer forGithubVaxData model."""

    class Meta:
        """Serialize all fields."""

        model = models.GithubVaxData
        fields = '__all__'