from rest_framework import generics
from drf_spectacular.utils import extend_schema
from config.mixins import CachedViewMixin
from .models import AdmissionYear
from .serializers import AdmissionYearListSerializer, AdmissionYearDetailSerializer


@extend_schema(tags=['Admission'])
class AdmissionYearListView(CachedViewMixin, generics.ListAPIView):
    """
    List all active admission years.
    """
    serializer_class = AdmissionYearListSerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        return AdmissionYear.objects.filter(
            is_active=True
        ).order_by('order', '-title')


@extend_schema(tags=['Admission'])
class AdmissionYearDetailView(CachedViewMixin, generics.RetrieveAPIView):
    """
    Retrieve a single admission year with its quotas.
    """
    serializer_class = AdmissionYearDetailSerializer
    authentication_classes = []
    permission_classes = []
    lookup_field = 'pk'

    def get_queryset(self):
        return AdmissionYear.objects.filter(
            is_active=True
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
