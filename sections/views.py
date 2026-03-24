from rest_framework import generics
from drf_spectacular.utils import extend_schema
from config.mixins import CachedViewMixin
from .models import Leader, StructureSection
from .serializers import (
    LeaderSerializer,
    StructureSectionSerializer,
    StructureSectionDetailSerializer,
)


@extend_schema(tags=['Leadership'])
class LeaderListView(CachedViewMixin, generics.ListAPIView):
    """
    List all active university leaders (Rahbariyat).

    Returns rector, pro-rectors, and other leaders
    ordered by their position rank.
    """
    serializer_class = LeaderSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return Leader.objects.filter(is_active=True).order_by('order', 'full_name')

    @extend_schema(
        summary="Rahbariyat ro'yxati",
        description="Universitetning barcha faol rahbarlari ro'yxatini qaytaradi.",
        responses={200: LeaderSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Structure'])
class StructureTreeView(CachedViewMixin, generics.ListAPIView):
    """
    List all top-level structure sections as a tree.

    Returns the university organizational structure with
    nested children, leaders, and members.
    """
    serializer_class = StructureSectionSerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = None  # Return full tree, no pagination

    def get_queryset(self):
        return (
            StructureSection.objects
            .filter(is_active=True, parent__isnull=True)
            .select_related('leader', 'leader__image')
            .prefetch_related(
                'members', 'members__image',
                'children', 'children__leader', 'children__leader__image',
                'children__members', 'children__members__image',
                'children__children', 'children__children__leader',
                'children__children__leader__image',
                'children__children__members',
                'children__children__members__image',
            )
            .order_by('order', 'name')
        )

    @extend_schema(
        summary="Universitet tuzilmasi",
        description=(
            "Universitetning tashkiliy tuzilmasini daraxt ko'rinishida qaytaradi. "
            "Har bir bo'lim o'z rahbari, a'zolari va ichki bo'limlari bilan."
        ),
        responses={200: StructureSectionSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Structure'])
class StructureSectionDetailView(CachedViewMixin, generics.RetrieveAPIView):
    """
    Retrieve a single structure section by slug.

    Returns full detail including description, leader,
    members, and child sections.
    """
    serializer_class = StructureSectionDetailSerializer
    authentication_classes = []
    permission_classes = []
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            StructureSection.objects
            .filter(is_active=True)
            .select_related('leader', 'leader__image')
            .prefetch_related(
                'members', 'members__image',
                'children', 'children__leader', 'children__leader__image',
                'children__members', 'children__members__image',
            )
        )

    @extend_schema(
        summary="Bo'lim tafsilotlari",
        description="Bitta tuzilma bo'limining to'liq ma'lumotlarini qaytaradi.",
        responses={200: StructureSectionDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
