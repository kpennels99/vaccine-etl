"""Github Vax data model definitions."""
from django.db import models


class GithubVaxData(models.Model):
    """Github Vaccination data model."""

    location = models.TextField(max_length=500, blank=True, null=True)
    iso_code = models.TextField(max_length=10, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    total_vaccinations = models.FloatField(blank=True, null=True)
    people_vaccinated = models.FloatField(blank=True, null=True)
    people_fully_vaccinated = models.FloatField(blank=True, null=True)
    daily_vaccinations_raw = models.FloatField(blank=True, null=True)
    daily_vaccinations = models.FloatField(blank=True, null=True)
    total_vaccinations_per_hundred = models.FloatField(blank=True, null=True)
    people_vaccinated_per_hundred = models.FloatField(blank=True, null=True)
    people_fully_vaccinated_per_hundred = models.FloatField(blank=True, null=True)
    daily_vaccinations_per_million = models.FloatField(blank=True, null=True)

    class Meta:
        """Model meta data attribute overrides."""

        managed = False
        db_table = 'github_vax_data'
