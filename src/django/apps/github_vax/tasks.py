from apps.github_vax.models import GithubVaxData, GraphReport
from celery.utils.log import get_task_logger
from api_config.celery import app
from datetime import datetime
import json 

from django.conf import settings

logger = get_task_logger(__file__)

def run_celery(callable_task, *args, **kwargs):
    """Run celery task."""
    # if  settings.DELAY_CELERY_TASKS:
    #     return callable_task.delay(*args, **kwargs)

    return callable_task(*args, **kwargs)

def validate_count(counts, index):
    prev_index = index
    while (prev_index := prev_index -1) >= 0:
        if counts[prev_index] is not None:
            return counts[prev_index]
        
    return counts[index]

def get_location_data(location, fields):
    print(f"getting location data for {location}")
    return location, GithubVaxData.objects.filter(location=location).only(*fields, 'date')\
                        .order_by('date')

def format_location_data(field, queryset):
    return {
        "x": list(queryset.values_list('date', flat=True)),
        "y": list(queryset.values_list(field, flat=True))
    }

@app.task
def generate_report_data(uuid):
    report = GraphReport.objects.get(pk=uuid)
    
    try:
        result = {
            field: {location: format_location_data(field, location_data)
                   for location, location_data in \
                map(get_location_data, report.locations, len(report.locations)*[report.vaccination_fields])}    
            for field in report.vaccination_fields
        }
        report.result = json.dumps(result)
        report.status = "success"
    except Exception as ex:
        logger.error(str(ex))
        report.status = "failed"
        report.result = {"error": str(ex)}
    
    report.save()