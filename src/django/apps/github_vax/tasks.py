"""Celery task definition."""
import json

from api_config.celery import app
from apps.github_vax.models import GithubVaxData
from apps.github_vax.models import GraphReport
from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger(__file__)


def run_celery(callable_task, *args, **kwargs):
    """Run celery task."""
    if settings.DELAY_CELERY_TASKS:
        return callable_task.delay(*args, **kwargs)

    return callable_task(*args, **kwargs)


def get_location_data(location, fields):
    """Filter GithubVaxData queryset by location and only retreive the specified fields."""
    logger.info(f'getting location data for {location}')
    filtered_queryset = GithubVaxData.objects.filter(location=location)\
        .only(*fields, 'date').order_by('date')
    return location, filtered_queryset


def format_location_data(field, queryset):
    """Convert queryset field and date to Plotly x y cordinaties."""
    return {
        'x': list(queryset.values_list('date', flat=True)),
        'y': list(queryset.values_list(field, flat=True))
    }


@app.task
def generate_report_data(uuid):
    """Run a GraphReport and Plotly format the results."""
    report = GraphReport.objects.get(pk=uuid)

    try:
        result = {
            field: {
                location: format_location_data(field, location_data)
                for location, location_data in
                map(get_location_data, report.locations,
                    len(report.locations)*[report.vaccination_fields])
            }
            for field in report.vaccination_fields
        }
        report.result = json.dumps(result, default=str)
        report.status = 'success'
    except Exception as ex:
        logger.error(str(ex))
        report.status = 'failed'
        report.result = {'error': str(ex)}

    report.save()
