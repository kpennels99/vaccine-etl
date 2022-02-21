"""Viewset definitions."""
from typing import Union

from django.http.response import HttpResponse, JsonResponse
from apps.core.okta_openid.permissions import OktaHasGraphingAccess
from django.http.request import HttpRequest
from apps.github_vax import filtersets
from apps.github_vax import models
from apps.github_vax import serializers
from apps.github_vax.tasks import generate_report_data
from apps.github_vax.tasks import run_celery
from django.shortcuts import render
from rest_framework import mixins
from rest_framework import renderers
from rest_framework import viewsets


class GithubVaxDataViewSet(viewsets.ReadOnlyModelViewSet):
    """PetFeature CRUD operations."""

    queryset = models.GithubVaxData.objects.all().order_by('-date')
    serializer_class = serializers.GithubVaxDataSerializer
    filterset_class = filtersets.GithubVaxDataFilter


class GraphReportViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin):
    """Create and retrieve report of vaccination data over time."""

    queryset = models.GraphReport.objects.all().order_by('-create_timestamp')
    serializer_class = serializers.GraphReportSerializer
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)
    permission_classes = [OktaHasGraphingAccess]

    def retrieve(self, request: HttpRequest, 
                 *args, **kwargs) -> Union[JsonResponse, HttpResponse]:
        """Return html graphing report result if the generation process was successful.
        
        If the Graph report data formatting was successful, return a HTML page as the 
        response, other return standard JSON response

        Args:
            request (HttpRequest): Incoming HTTP request.

        Returns:
            Union[JsonResponse, HttpResponse]: HTML or JSON response depending on current 
                status of report result
        """
        instance = self.get_object()
        if instance.status == 'success':
            return render(request, 'graph.html', {'data': instance.result})
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer: serializers.GithubVaxDataSerializer):
        """Create model instance and run the corresponding report."""
        graph_report = serializer.save()
        print("running celery")
        run_celery(generate_report_data, graph_report.pk)
        print("celery run")
