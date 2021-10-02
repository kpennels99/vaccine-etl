"""Serializer definitions."""
from apps.github_vax import models
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class GithubVaxDataSerializer(serializers.ModelSerializer):
    """Basic serializer forGithubVaxData model."""

    class Meta:
        """Serialize all fields."""

        model = models.GithubVaxData
        fields = '__all__'


class GraphReportSerializer(serializers.ModelSerializer):
    """Basic serializer forGithubVaxData model."""

    class Meta:
        """Serializer Meta overrides."""

        model = models.GraphReport
        fields = '__all__'
        read_only_fields = ['status', 'result', 'created_by']

    def create(self, validated_data):
        """Override ``create`` to provide a created_by via request.user by default."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def validate_locations(self, value_array):
        """Ensure all locations exists in GithubVaxData model."""
        for location in value_array:
            if not models.GithubVaxData.objects.filter(location=location).exists():
                raise ValidationError(f"{location} doesn't exist in GithubVaxData model.")

        return list(set(value_array))

    def validate_regions(self, value_array):
        """Ensure all regions exists in GithubVaxData model."""
        for region in value_array:
            if not models.GithubVaxData.objects.filter(region=region).exists():
                raise ValidationError(f'{region} does not exist in GithubVaxData model.')

        return list(set(value_array))

    def validate_sub_regions(self, value_array):
        """Ensure all sub_regions exists in GithubVaxData model."""
        for sub_region in value_array:
            if not models.GithubVaxData.objects.filter(sub_region=sub_region).exists():
                raise ValidationError(
                    f"{sub_region} doesn't exist in GithubVaxData model."
                )

        return list(set(value_array))

    def validate_intermediate_regions(self, value_array):
        """Ensure all sub_regions exists in GithubVaxData model."""
        for intermediate_region in value_array:
            if not models.GithubVaxData.objects.filter(
                        intermediate_region=intermediate_region
                    ).exists():
                raise ValidationError(f'Intermediate region {intermediate_region}'
                                      'does not exist in GithubVaxData model.')

        return list(set(value_array))

    def validate_vaccination_fields(self, value_array):
        """Ensure all vaccination tally fields exists in GithubVaxData model."""
        model_fields = [field.name for field in models.GithubVaxData._meta.get_fields()]
        valid_fields = set(model_fields) - set(['location', 'iso_code', 'date', 'region',
                                                'sub_region', 'intermediate_region'])
        for field in value_array:
            if field not in valid_fields:
                raise ValidationError(f'{field}: does not exist in GithubVaxData model.')

        return list(set(value_array))
