"""Github Vax data model definitions."""
import uuid

from django.contrib.auth import get_user_model
from django.contrib.postgres import fields as postgres_fields
from django.db import models


class GithubVaxData(models.Model):
    """Github Vaccination data model."""

    # TODO: Add github owid descriptions
    location = models.CharField(max_length=500, blank=True, null=True)
    iso_code = models.CharField(max_length=10, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    total_vaccinations = models.FloatField(blank=True, null=True)
    people_vaccinated = models.FloatField(blank=True, null=True)
    people_fully_vaccinated = models.FloatField(blank=True, null=True)
    total_boosters = models.FloatField(blank=True, null=True)

    daily_vaccinations_raw = models.FloatField(blank=True, null=True)
    daily_vaccinations = models.FloatField(blank=True, null=True)
    total_vaccinations_per_hundred = models.FloatField(blank=True, null=True)
    people_vaccinated_per_hundred = models.FloatField(blank=True, null=True)
    people_fully_vaccinated_per_hundred = models.FloatField(blank=True, null=True)
    total_boosters_per_hundred = models.FloatField(blank=True, null=True)
    daily_vaccinations_per_million = models.FloatField(blank=True, null=True)
    region = models.CharField(max_length=200, blank=True, null=True)
    sub_region = models.CharField(max_length=200, blank=True, null=True)
    intermediate_region = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        """Model meta data attribute overrides."""

        db_table = 'github_vax_data'


class GraphReport(models.Model):
    """Graph report meta data."""

    status_choices = (
        ('PENDING', 'pending'),
        ('SUCCESS', 'success'),
        ('FAILURE', 'failure')
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    locations = postgres_fields.ArrayField(
        models.CharField(max_length=200, blank=False, null=False), default=list
    )
    regions = postgres_fields.ArrayField(
        models.CharField(max_length=200, blank=False, null=False), default=list
    )
    sub_regions = postgres_fields.ArrayField(
        models.CharField(max_length=200, blank=False, null=False), default=list
    )
    intermediate_regions = postgres_fields.ArrayField(
        models.CharField(max_length=200, blank=False, null=False), default=list
    )
    vaccination_fields = postgres_fields.ArrayField(
        models.CharField(max_length=200, blank=False, null=False), default=list
    )
    status = models.CharField(max_length=124, choices=status_choices,
                              default=status_choices[0][1])
    result = models.JSONField(default=dict, null=True, blank=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    create_timestamp = models.DateTimeField(auto_now_add=True)
    update_timestamp = models.DateTimeField(auto_now=True)
