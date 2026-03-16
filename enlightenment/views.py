from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import AchievementSection, EnlightenmentSection, Club
from .serializers import (
    AchievementSectionSerializer,
    EnlightenmentSectionSerializer,
    ClubListSerializer,
    ClubDetailSerializer,
)


@extend_schema(tags=['Enlightenment'])
class AchievementSectionListView(generics.ListAPIView):
    """
    List all active achievement sections ("Yuksak marralar").

    Returns ordered content blocks for the Achievements page.
    """
    serializer_class = AchievementSectionSerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        return (
            AchievementSection.objects
            .filter(is_active=True)
            .select_related('cover_image')
            .order_by('order', 'title')
        )

    @extend_schema(
        summary="Yutuqlar bo'limlari",
        description="'Yuksak marralar' sahifasi uchun barcha faol bo'limlarni qaytaradi.",
        responses={200: AchievementSectionSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Enlightenment'])
class EnlightenmentSectionListView(generics.ListAPIView):
    """
    List all active enlightenment sections ("Ma'rifiy muhit").

    Returns ordered content blocks for the Enlightenment page.
    """
    serializer_class = EnlightenmentSectionSerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        return (
            EnlightenmentSection.objects
            .filter(is_active=True)
            .select_related('cover_image')
            .order_by('order', 'title')
        )

    @extend_schema(
        summary="Ma'rifat bo'limlari",
        description="'Ma'rifiy muhit' sahifasi uchun barcha faol bo'limlarni qaytaradi.",
        responses={200: EnlightenmentSectionSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Enlightenment'])
class ClubListView(generics.ListAPIView):
    """
    List all active clubs and circles.

    Returns clubs like "Zakovat Klub", "Teatr Studiyasi", etc.
    """
    serializer_class = ClubListSerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        return (
            Club.objects
            .filter(is_active=True)
            .select_related('cover_image')
            .order_by('order', 'name')
        )

    @extend_schema(
        summary="Klublar ro'yxati",
        description="Barcha faol klub va to'garaklar ro'yxatini qaytaradi.",
        responses={200: ClubListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Enlightenment'])
class ClubDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single club by slug.

    Returns full detail including rich-text content.
    """
    serializer_class = ClubDetailSerializer
    authentication_classes = []
    permission_classes = []
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Club.objects
            .filter(is_active=True)
            .select_related('cover_image')
        )

    @extend_schema(
        summary="Klub tafsilotlari",
        description="Bitta klubning to'liq ma'lumotlarini qaytaradi.",
        responses={200: ClubDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Enlightenment'])
class StatsView(APIView):
    """
    Return dynamic stats for the Achievements page sidebar.

    Counts partners, projects, and collaboration types from the collaboration app.
    """
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Filial statistikasi",
        description="Hamkorlar, loyihalar va dasturlar sonini qaytaradi.",
    )
    def get(self, request, *args, **kwargs):
        from collaboration.models import PartnerOrganization, CollaborationProject, CollaborationType

        partners_count = PartnerOrganization.objects.filter(is_active=True).count()
        projects_count = CollaborationProject.objects.filter(is_active=True).count()
        programs_count = CollaborationType.objects.filter(is_active=True).count()

        return Response({
            'partners_count': partners_count,
            'projects_count': projects_count,
            'programs_count': programs_count,
        })

