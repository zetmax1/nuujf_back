from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.throttling import AnonRateThrottle
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Vacancy, VacancyApplication
from .serializers import (
    VacancyListSerializer,
    VacancyDetailSerializer,
    VacancyApplicationSerializer,
)


# ============================================
# SECURITY: Custom throttle classes
# ============================================

class ApplicationBurstThrottle(AnonRateThrottle):
    """Limit rapid-fire submissions: max 3 per minute per IP"""
    rate = '3/min'
    scope = 'vacancy_apply_burst'


class ApplicationDailyThrottle(AnonRateThrottle):
    """Limit total daily submissions: max 10 per day per IP"""
    rate = '10/day'
    scope = 'vacancy_apply_daily'


@extend_schema(tags=['Vacancies'])
class VacancyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for university vacancies.

    List and retrieve active vacancy postings.
    Supports filtering by category.
    """
    queryset = Vacancy.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return VacancyListSerializer
        return VacancyDetailSerializer

    @extend_schema(
        summary="List all active vacancies",
        description="Retrieve a list of all active vacancies with optional category filtering.",
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by category: academic, technical, admin",
                required=False,
                examples=[
                    OpenApiExample('Pedagogik', value='academic'),
                    OpenApiExample('Texnik', value='technical'),
                    OpenApiExample("Ma'muriy", value='admin'),
                ]
            ),
        ],
        responses={200: VacancyListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get vacancy detail",
        description="Retrieve detailed information about a specific vacancy.",
        responses={200: VacancyDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category in ['academic', 'technical', 'admin']:
            queryset = queryset.filter(category=category)
        return queryset


@extend_schema(tags=['Vacancies'])
class VacancyApplicationCreateView(generics.CreateAPIView):
    """
    Submit an application for a vacancy.

    No authentication required — public form submission.
    Accepts multipart/form-data for resume uploads.

    Security measures:
    - Rate limiting: 3 requests/min, 10 requests/day per IP
    - File validation: extension + MIME type + size check
    - Input sanitization: HTML stripping, length limits
    - Only accepts multipart/form-data (no raw JSON for file uploads)
    """
    serializer_class = VacancyApplicationSerializer
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = []
    permission_classes = []
    throttle_classes = [ApplicationBurstThrottle, ApplicationDailyThrottle]

    @extend_schema(
        summary="Apply for a vacancy",
        description=(
            "Submit a job application. Resume is required (PDF/DOC/DOCX, max 5MB). "
            "Rate-limited to 3 requests per minute and 10 per day per IP."
        ),
        responses={201: VacancyApplicationSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        return Response(
            {
                'status': 'success',
                'message': "Arizangiz muvaffaqiyatli yuborildi!",
                'application': VacancyApplicationSerializer(application).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def throttled(self, request, wait):
        """Custom throttle error message in Uzbek"""
        from rest_framework.exceptions import Throttled
        raise Throttled(
            detail={
                'message': "Juda ko'p so'rov yubordingiz. Iltimos, biroz kuting.",
                'wait_seconds': int(wait),
            }
        )
