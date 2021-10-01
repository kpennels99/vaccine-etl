"""Viewset definitions."""
from apps.core.okta_openid.permissions import OktaHasGraphingAccess
from apps.github_vax import filtersets
from apps.github_vax import models
from apps.github_vax import serializers
from rest_framework import viewsets, renderers
from rest_framework import mixins
from django.shortcuts import render

from apps.github_vax.tasks import run_celery, generate_report_data


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
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve report as html page graphing the results over time."""
        instance = self.get_object()
        if instance.status == 'success':
            return render(request, 'graph.html', {"data": instance.result})
        return super().retrieve(request, *args, **kwargs)
    

    def perform_create(self, serializer):
        """Create model instance and run the corresponding report."""
        graph_report = serializer.save()
        run_celery(generate_report_data, graph_report.pk)