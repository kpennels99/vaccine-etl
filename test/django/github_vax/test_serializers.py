from django.http.request import HttpRequest

import pytest 

from apps.github_vax.serializers import GraphReportSerializer

@pytest.fixture
def valid_graph_report_payload():
    return {"locations": ["South Africa"],
            "regions": ["Africa"],
            "sub_regions": ["Sub-Saharan Africa"],
            "intermediate_regions": ["Southern Africa"],
            "vaccination_fields": ["people_fully_vaccinated"]}
    

@pytest.fixture
def valid_serializer_request(logged_in_user):
    request = HttpRequest()
    request.user = logged_in_user
    return request

@pytest.mark.django_db
def test_graph_report_create(valid_serializer_request, valid_graph_report_payload):
    """Ensure created by is added to validated data before creation."""
    graph_report_serializer = GraphReportSerializer(
        data=valid_graph_report_payload,
        context={"request": valid_serializer_request}
    )
    graph_report_serializer.is_valid(raise_exception=True)
    instance = graph_report_serializer.save()
    assert instance.created_by == valid_serializer_request.user
    
    
@pytest.mark.django_db
def test_graph_report_locations(valid_graph_report_payload):
    """Ensure created by is added to validated data before creation."""
    graph_report_serializer = GraphReportSerializer(
        data=valid_graph_report_payload,
        context={"request": valid_graph_report_payload}
    )
    graph_report_serializer.is_valid(raise_exception=True)
    assert graph_report_serializer.validated_data["locations"] == \
        valid_graph_report_payload["locations"]
    

@pytest.mark.django_db
def test_graph_report_regions(valid_graph_report_payload):
    """Ensure created by is added to validated data before creation."""
    graph_report_serializer = GraphReportSerializer(
        data=valid_graph_report_payload,
        context={"request": valid_graph_report_payload}
    )
    graph_report_serializer.is_valid(raise_exception=True)
    print(graph_report_serializer.validated_data)
    assert graph_report_serializer.validated_data["regions"] == \
        valid_graph_report_payload["regions"]
        
        
@pytest.mark.django_db
def test_graph_report_sub_regions(valid_graph_report_payload):
    """Ensure created by is added to validated data before creation."""
    graph_report_serializer = GraphReportSerializer(
        data=valid_graph_report_payload,
        context={"request": valid_graph_report_payload}
    )
    graph_report_serializer.is_valid(raise_exception=True)
    assert graph_report_serializer.validated_data["sub_regions"] == \
        valid_graph_report_payload["sub_regions"]
        

@pytest.mark.django_db
def test_graph_report_intermediate_regions(valid_graph_report_payload):
    """Ensure created by is added to validated data before creation."""
    graph_report_serializer = GraphReportSerializer(
        data=valid_graph_report_payload,
        context={"request": valid_graph_report_payload}
    )
    graph_report_serializer.is_valid(raise_exception=True)
    assert graph_report_serializer.validated_data["intermediate_regions"] == \
        valid_graph_report_payload["intermediate_regions"]


@pytest.mark.django_db
def test_graph_report_vaccination_fields(valid_graph_report_payload):
    """Ensure created by is added to validated data before creation."""
    graph_report_serializer = GraphReportSerializer(
        data=valid_graph_report_payload,
        context={"request": valid_graph_report_payload}
    )
    graph_report_serializer.is_valid(raise_exception=True)
    assert graph_report_serializer.validated_data["vaccination_fields"] == \
        valid_graph_report_payload["vaccination_fields"]