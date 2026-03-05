from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import AdmissionYear
from .serializers import AdmissionYearListSerializer, AdmissionYearDetailSerializer


@extend_schema(tags=['Admission'])
class AdmissionYearListView(generics.ListAPIView):
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

    @extend_schema(
        summary="Qabul yillari ro'yxati",
        description="Barcha faol qabul yillarini qaytaradi.",
        responses={200: AdmissionYearListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Admission'])
class AdmissionYearDetailView(generics.RetrieveAPIView):
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
        ).prefetch_related('quotas')

    @extend_schema(
        summary="Qabul yili tafsilotlari",
        description="Bitta qabul yilining to'liq ma'lumotlari va kvotalarini qaytaradi.",
        responses={200: AdmissionYearDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
