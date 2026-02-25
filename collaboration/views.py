from rest_framework import generics
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import CollaborationType, PartnerOrganization, CollaborationProject
from .serializers import (
    CollaborationTypeListSerializer,
    CollaborationTypeDetailSerializer,
    PartnerOrganizationListSerializer,
    PartnerOrganizationDetailSerializer,
    CollaborationProjectListSerializer,
    CollaborationProjectDetailSerializer,
)


# ============================================
# COLLABORATION TYPE VIEWS
# ============================================

@extend_schema(tags=['Collaboration'])
class CollaborationTypeListView(generics.ListAPIView):
    """
    List all active collaboration types.

    Returns types like "Xalqaro hamkor tashkilotlar",
    "Almashinuv dasturlari", etc.
    """
    serializer_class = CollaborationTypeListSerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        return CollaborationType.objects.filter(
            is_active=True
        ).select_related('cover_image').order_by('order', 'title')

    @extend_schema(
        summary="Hamkorlik turlari ro'yxati",
        description="Barcha faol hamkorlik turlarini qaytaradi.",
        responses={200: CollaborationTypeListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Collaboration'])
class CollaborationTypeDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single collaboration type by slug.

    Returns the type with its partners and projects.
    """
    serializer_class = CollaborationTypeDetailSerializer
    authentication_classes = []
    permission_classes = []
    lookup_field = 'slug'

    def get_queryset(self):
        return CollaborationType.objects.filter(
            is_active=True
        ).select_related('cover_image').prefetch_related(
            'partners', 'partners__logo', 'partners__collaboration_type',
            'projects', 'projects__cover_image', 'projects__collaboration_type',
        )

    @extend_schema(
        summary="Hamkorlik turi tafsilotlari",
        description="Bitta hamkorlik turining to'liq ma'lumotlarini, hamkorlarini va loyihalarini qaytaradi.",
        responses={200: CollaborationTypeDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ============================================
# PARTNER ORGANIZATION VIEWS
# ============================================

@extend_schema(tags=['Collaboration'])
class PartnerOrganizationListView(generics.ListAPIView):
    """
    List all active partner organizations.

    Supports filtering by collaboration type slug and country.
    """
    serializer_class = PartnerOrganizationListSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        qs = PartnerOrganization.objects.filter(
            is_active=True
        ).select_related('collaboration_type', 'logo').order_by('order', 'name')

        # Filter by collaboration type slug
        type_slug = self.request.query_params.get('type')
        if type_slug:
            qs = qs.filter(collaboration_type__slug=type_slug)

        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            qs = qs.filter(country__icontains=country)

        return qs

    @extend_schema(
        summary="Hamkor tashkilotlar ro'yxati",
        description="Barcha faol hamkor tashkilotlarni qaytaradi. type va country parametrlari bilan filter qilish mumkin.",
        parameters=[
            OpenApiParameter(name='type', description='Hamkorlik turi slug-i bo\'yicha filter', type=str),
            OpenApiParameter(name='country', description='Davlat nomi bo\'yicha filter', type=str),
        ],
        responses={200: PartnerOrganizationListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Collaboration'])
class PartnerOrganizationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single partner organization by slug.
    """
    serializer_class = PartnerOrganizationDetailSerializer
    authentication_classes = []
    permission_classes = []
    lookup_field = 'slug'

    def get_queryset(self):
        return PartnerOrganization.objects.filter(
            is_active=True
        ).select_related('collaboration_type', 'logo')

    @extend_schema(
        summary="Hamkor tashkilot tafsilotlari",
        description="Bitta hamkor tashkilotning to'liq ma'lumotlarini qaytaradi.",
        responses={200: PartnerOrganizationDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ============================================
# COLLABORATION PROJECT VIEWS
# ============================================

@extend_schema(tags=['Collaboration'])
class CollaborationProjectListView(generics.ListAPIView):
    """
    List all active collaboration projects.

    Supports filtering by collaboration type slug.
    """
    serializer_class = CollaborationProjectListSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        qs = CollaborationProject.objects.filter(
            is_active=True
        ).select_related('collaboration_type', 'cover_image').order_by('order', 'title')

        # Filter by collaboration type slug
        type_slug = self.request.query_params.get('type')
        if type_slug:
            qs = qs.filter(collaboration_type__slug=type_slug)

        return qs

    @extend_schema(
        summary="Hamkorlik loyihalari ro'yxati",
        description="Barcha faol hamkorlik loyihalarini qaytaradi. type parametri bilan filter qilish mumkin.",
        parameters=[
            OpenApiParameter(name='type', description='Hamkorlik turi slug-i bo\'yicha filter', type=str),
        ],
        responses={200: CollaborationProjectListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Collaboration'])
class CollaborationProjectDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single collaboration project by slug.

    Returns full content with linked partners.
    """
    serializer_class = CollaborationProjectDetailSerializer
    authentication_classes = []
    permission_classes = []
    lookup_field = 'slug'

    def get_queryset(self):
        return CollaborationProject.objects.filter(
            is_active=True
        ).select_related(
            'collaboration_type', 'cover_image'
        ).prefetch_related(
            'partners', 'partners__logo', 'partners__collaboration_type',
        )

    @extend_schema(
        summary="Hamkorlik loyihasi tafsilotlari",
        description="Bitta hamkorlik loyihasining to'liq mazmuni va hamkorlarini qaytaradi.",
        responses={200: CollaborationProjectDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
