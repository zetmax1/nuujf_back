from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.db.models import Count, Q
from config.mixins import CachedViewMixin

from .models import Faculty, Department
from .serializers import (
    FacultyListSerializer, FacultyDetailSerializer,
    DepartmentListSerializer, DepartmentDetailSerializer,
)


@extend_schema(tags=['Faculties'])
class FacultyViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for university faculties.

    List returns lightweight data; detail returns full data including
    nested departments and achievements.
    """
    authentication_classes = []
    permission_classes = []

    def get_serializer_class(self):
        if self.action == 'list':
            return FacultyListSerializer
        return FacultyDetailSerializer

    def get_queryset(self):
        queryset = Faculty.objects.filter(is_active=True)

        if self.action == 'retrieve':
            queryset = queryset.select_related(
                'cover_image', 'dean_image'
            ).prefetch_related(
                'achievements', 'departments'
            )
        else:
            queryset = queryset.select_related('cover_image').annotate(
                active_departments_count=Count('departments', filter=Q(departments__is_active=True))
            )

        return queryset

    @extend_schema(
        summary="Fakultetlar ro'yxati",
        description="Barcha faol fakultetlarni qaytaradi.",
        responses={200: FacultyListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Fakultet tafsilotlari",
        description="Bitta fakultetning to'liq ma'lumotlarini qaytaradi (kafedralar va yutuqlar bilan).",
        responses={200: FacultyDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Fakultetni kod bo'yicha olish",
        parameters=[
            OpenApiParameter(
                name='code',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Fakultet kodi',
                required=True,
            ),
        ],
        responses={
            200: FacultyDetailSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        }
    )
    @action(detail=False, methods=['get'])
    def by_code(self, request):
        """Get faculty by code: /api/faculties/by_code/?code=KI"""
        code = request.query_params.get('code')

        if not code:
            return Response({'error': 'Code parameter is required'}, status=400)

        try:
            faculty = Faculty.objects.filter(is_active=True).select_related(
                'cover_image', 'dean_image'
            ).prefetch_related(
                'achievements', 'departments'
            ).get(faculty_code=code)
            serializer = FacultyDetailSerializer(faculty, context={'request': request})
            return Response(serializer.data)
        except Faculty.DoesNotExist:
            return Response({'error': 'Faculty not found'}, status=404)


@extend_schema(tags=['Departments'])
class DepartmentViewSet(CachedViewMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for university departments.

    List returns lightweight data; detail returns full data including
    nested programs, subjects, staff, and publications — all in one API call.
    """
    authentication_classes = []
    permission_classes = []

    def get_serializer_class(self):
        if self.action == 'list':
            return DepartmentListSerializer
        return DepartmentDetailSerializer

    def get_queryset(self):
        queryset = Department.objects.filter(is_active=True)

        # Filter by faculty if provided
        faculty_id = self.request.query_params.get('faculty')
        if faculty_id:
            queryset = queryset.filter(faculty_id=faculty_id)

        if self.action == 'retrieve':
            queryset = queryset.select_related(
                'faculty', 'cover_image', 'head_image'
            ).prefetch_related(
                'programs', 'subjects', 'staff', 'publications'
            )
        else:
            queryset = queryset.select_related('faculty', 'cover_image')

        return queryset

    @extend_schema(
        summary="Kafedralar ro'yxati",
        description="Barcha faol kafedralarni qaytaradi. Fakultet bo'yicha filtrlash mumkin.",
        parameters=[
            OpenApiParameter(
                name='faculty',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Fakultet ID bo\'yicha filtrlash',
                required=False,
            ),
        ],
        responses={200: DepartmentListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Kafedra tafsilotlari",
        description="Bitta kafedraning to'liq ma'lumotlarini qaytaradi (dasturlar, fanlar, xodimlar, nashrlar bilan).",
        responses={200: DepartmentDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Kafedrani kod bo'yicha olish",
        parameters=[
            OpenApiParameter(
                name='code',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Kafedra kodi (masalan: ATDT)',
                required=True,
                examples=[
                    OpenApiExample('Software Engineering', value='ATDT'),
                ],
            ),
        ],
        responses={
            200: DepartmentDetailSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        }
    )
    @action(detail=False, methods=['get'])
    def by_code(self, request):
        """Get department by code: /api/departments/by_code/?code=ATDT"""
        code = request.query_params.get('code')

        if not code:
            return Response({'error': 'Code parameter is required'}, status=400)

        try:
            department = Department.objects.filter(is_active=True).select_related(
                'faculty', 'cover_image', 'head_image'
            ).prefetch_related(
                'programs', 'subjects', 'staff', 'publications'
            ).get(department_code=code)
            serializer = DepartmentDetailSerializer(department, context={'request': request})
            return Response(serializer.data)
        except Department.DoesNotExist:
            return Response({'error': 'Department not found'}, status=404)