import rest_framework_filters as filters

from . import models

class GithubVaxDataFilter(filters.FilterSet):
    """Custom PetFollowViewset filters."""

    class Meta:
        """Filter type definition."""

        model = models.GithubVaxData
        fields = {
            'date': ['gte', 'lte'],
            'location': ['exact', 'icontains'],
            'iso_code': ['exact', 'icontains'],
            'total_vaccinations': ['gte', 'lte'],
            'people_vaccinated': ['gte', 'lte'],
            'people_fully_vaccinated': ['gte', 'lte'],
            'daily_vaccinations_raw': ['gte', 'lte'],
            'daily_vaccinations': ['gte', 'lte'],
        }