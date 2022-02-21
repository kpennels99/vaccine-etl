import json
from apps.github_vax.tasks import generate_report_data
from apps.github_vax.models import GraphReport
from apps.github_vax.tasks import format_location_data
from apps.github_vax.tasks import get_location_data
from apps.github_vax.tasks import run_celery
from django.http.request import HttpRequest

import pytest 

from apps.github_vax.serializers import GraphReportSerializer
from apps.github_vax.models import GithubVaxData

def test_run_celery(settings):
    """Ensure created by is added to validated data before creation."""
    settings.DELAY_CELERY_TASKS = False
    func = lambda x: x + 1
    assert run_celery(func, 1) == 2
   
   
@pytest.mark.django_db 
def test_get_location_data():
    location, filtered_queryset = get_location_data("South Africa", ["id"])
    assert location == "South Africa"
    sample = filtered_queryset[0]
    excluded_fields = [field.name for field in GithubVaxData._meta.get_fields()
                       if field.name not in ["id", "date"]]
    for field in excluded_fields:
        assert field in sample.get_deferred_fields()
        

@pytest.mark.django_db 
def test_format_location_data():
    """Test whether queryset fields and date are converted to Plotly x y cordinaties."""
    _, filtered_queryset = get_location_data("South Africa", ["id"])
    expected_data = {
        "x": [item.date for item in filtered_queryset],
        "y": [item.id for item in filtered_queryset]
    }
    assert format_location_data("id", filtered_queryset) == expected_data
    

@pytest.mark.django_db 
def test_generate_report_data(logged_in_user):
    """Test whether report contains the expected fields and reports a success."""
    location = "South Africa"
    vaccination_fields = "people_vaccinated"
    data = GithubVaxData.objects.filter(location=location)
    assert data.exists()
    assert len(data) == 11
    report = GraphReport.objects.create(locations=[location],
                                        vaccination_fields=[vaccination_fields],
                                        created_by=logged_in_user)
    generate_report_data(uuid=report.uuid)
    report.refresh_from_db()
    assert report.status == "success"
    expected_data = {
        vaccination_fields: {
            location: 
                {
                    "x" : [row.date for row in data],
                    "y": [getattr(row, vaccination_fields) for row in data]
                }
        }
    }
    print(expected_data, report.result)
    assert report.result == json.dumps(expected_data, default=str)