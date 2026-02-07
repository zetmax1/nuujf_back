from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import FacultyPage, DepartmentPage
from .serializers import FacultyPageSerializer, DepartmentPageSerializer, DepartmentPageListSerializer


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FacultyPage.objects.live().public()
    serializer_class = FacultyPageSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by locale/language
        locale = self.request.query_params.get('locale', 'uz')
        queryset = queryset.filter(locale__language_code=locale)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_code(self, request):
        """Get faculty by code: /api/faculties/by_code/?code=KI"""
        code = request.query_params.get('code')
        locale = request.query_params.get('locale', 'uz')
        
        try:
            faculty = FacultyPage.objects.live().public().get(
                faculty_code=code,
                locale__language_code=locale
            )
            serializer = self.get_serializer(faculty)
            return Response(serializer.data)
        except FacultyPage.DoesNotExist:
            return Response({'error': 'Faculty not found'}, status=404)


@extend_schema(tags=['Departments'])
class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for managing university departments.
    
    Provides listing, detail view, and filtering capabilities for departments.
    All departments support multilingual content.
    """
    queryset = DepartmentPage.objects.live().public()
    serializer_class = DepartmentPageSerializer
    
    def get_serializer_class(self):
        # Use lighter serializer for list view
        if self.action == 'list':
            return DepartmentPageListSerializer
        return DepartmentPageSerializer
    
    @extend_schema(
        summary="List all departments",
        description="Retrieve a paginated list of all active departments. Can be filtered by locale and faculty.",
        parameters=[
            OpenApiParameter(
                name='locale',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Language code (uz, en, ru)',
                required=False,
                examples=[
                    OpenApiExample('Uzbek', value='uz'),
                    OpenApiExample('English', value='en'),
                    OpenApiExample('Russian', value='ru'),
                ]
            ),
            OpenApiParameter(
                name='faculty',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter departments by faculty ID',
                required=False,
            ),
        ],
        responses={200: DepartmentPageListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get department detail",
        description="Retrieve detailed information about a specific department including programs, subjects, staff, and publications.",
        responses={200: DepartmentPageSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by locale/language
        locale = self.request.query_params.get('locale', 'uz')
        queryset = queryset.filter(locale__language_code=locale)
        
        # Filter by faculty if provided
        faculty_id = self.request.query_params.get('faculty')
        if faculty_id:
            queryset = queryset.filter(faculty_id=faculty_id)
        
        # Optimize queries
        queryset = queryset.select_related('faculty')
        
        # For detail view, prefetch related data
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'programs', 'subjects', 'staff', 'publications'
            )
        
        return queryset
    
    @extend_schema(
        summary="Get department by code",
        description="Retrieve a department by its unique department code.",
        parameters=[
            OpenApiParameter(
                name='code',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Department code (e.g., ATDT)',
                required=True,
                examples=[
                    OpenApiExample('Software Engineering', value='ATDT'),
                ]
            ),
            OpenApiParameter(
                name='locale',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Language code (uz, en, ru)',
                required=False,
            ),
        ],
        responses={
            200: DepartmentPageSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        }
    )
    @action(detail=False, methods=['get'])
    def by_code(self, request):
        """Get department by code: /api/faculties/departments/by_code/?code=ATDT"""
        code = request.query_params.get('code')
        locale = request.query_params.get('locale', 'uz')
        
        if not code:
            return Response({'error': 'Code parameter is required'}, status=400)
        
        try:
            department = DepartmentPage.objects.live().public().prefetch_related(
                'programs', 'subjects', 'staff', 'publications'
            ).get(
                department_code=code,
                locale__language_code=locale
            )
            serializer = DepartmentPageSerializer(department)
            return Response(serializer.data)
        except DepartmentPage.DoesNotExist:
            return Response({'error': 'Department not found'}, status=404)