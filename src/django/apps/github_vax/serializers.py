"""Serializer definitions."""
from rest_framework.exceptions import ValidationError
from apps.github_vax import models
from rest_framework import serializers


class GithubVaxDataSerializer(serializers.ModelSerializer):
    """Basic serializer forGithubVaxData model."""

    class Meta:
        """Serialize all fields."""

        model = models.GithubVaxData
        fields = '__all__'

class GraphReportCountrySerializer(serializers.Serializer):
    country = serializers.CharField()
    
    def validate_country(self, value):
        value = super().validate_country(value)
        if not models.GithubVaxData.objects.filter(location=value).exists():
            return ValidationError("Country does not exist in OWID repository")
        
        # check if supplementary country data exists
        return value


class GraphReportSerializer(serializers.ModelSerializer):
    """Basic serializer forGithubVaxData model."""
    
    class Meta:
        """Serialize all fields."""

        model = models.GraphReport
        fields = '__all__'
        read_only_fields = ['status', 'result', 'created_by']
        
    def create(self, validated_data):
        """Override ``create`` to provide a created_by via request.user by default.
        """
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
        
    def validate_locations(self, value_array): 
        for location in value_array:
            if not models.GithubVaxData.objects.filter(location=location).exists():
                raise ValidationError(f"{location}: does not exist in GithubVaxData model.")
        
        return list(set(value_array))
    
    def validate_vaccination_fields(self, value_array): 
        model_fields = [field.name for field in models.GithubVaxData._meta.get_fields()]
        valid_fields = set(model_fields) - set(["location", "iso_code", "date"])
        for field in value_array:
            if not field in valid_fields:
                raise ValidationError(f"{field}: does not exist in GithubVaxData model.")
        
        return list(set(value_array))
    
    def validate_regions(self, value_array): 
        for region in value_array:
            if not models.GithubVaxData.objects.filter(region=region).exists():
                raise ValidationError(f"Region {region} does not exist in GithubVaxData model.")
        
        return list(set(value_array))
    
    def validate_sub_regions(self, value_array): 
        for sub_region in value_array:
            if not models.GithubVaxData.objects.filter(sub_region=sub_region).exists():
                raise ValidationError(f"Sub region {sub_region} does not exist in GithubVaxData model.")
        
        return list(set(value_array))

    def validate_intermediate_regions(self, value_array): 
        for intermediate_region in value_array:
            if not models.GithubVaxData.objects.filter(
                intermediate_region=intermediate_region).exists():
                raise ValidationError(f"Intermediate region {intermediate_region} does not exist in "
                                      "GithubVaxData model.")
        
        return list(set(value_array))