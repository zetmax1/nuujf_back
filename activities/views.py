from rest_framework import generics
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema
from config.mixins import CachedViewMixin
from .models import ActivityCategory, ActivityPage
from .serializers import (
    ActivityCategoryListSerializer,
    ActivityCategoryDetailSerializer,
    ActivityPageDetailSerializer,
)


class ActivityCategoryListView(CachedViewMixin, generics.ListAPIView):
    """
    List all active activity categories.

    Returns categories like "O'quv faoliyati", "Ilmiy faoliyat", etc.
    """
    serializer_class = ActivityCategoryListSerializer
    authentication_classes = []
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        return ActivityCategory.objects.filter(
            is_active=True
        ).select_related('cover_image').order_by('order', 'title')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ActivityCategoryDetailView(CachedViewMixin, generics.RetrieveAPIView):
    """
    Retrieve a single activity category by slug.

    Returns the category with its description and
    direct child pages (first-level pages).
    """
    serializer_class = ActivityCategoryDetailSerializer
    authentication_classes = []
    permission_classes = []
    lookup_field = 'slug'

    def get_queryset(self):
        return ActivityCategory.objects.filter(
            is_active=True
        ).select_related('cover_image').prefetch_related(
            'pages', 'pages__cover_image', 'pages__children',
        )

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=['Activities'])
class ActivityPageDetailView(CachedViewMixin, generics.RetrieveAPIView):
    """
    Retrieve a single activity page by category slug and page slug.

    Returns full content, child pages, and breadcrumb trail.
    Works for pages at any nesting depth.
    """
    serializer_class = ActivityPageDetailSerializer
    authentication_classes = []
    permission_classes = []

    def get_object(self):
        category_slug = self.kwargs['category_slug']
        page_slug = self.kwargs['page_slug']
        try:
            page = (
                ActivityPage.objects
                .filter(is_active=True, category__is_active=True)
                .select_related('category', 'parent', 'cover_image')
                .prefetch_related('children', 'children__cover_image')
                .get(category__slug=category_slug, slug=page_slug)
            )
        except ActivityPage.DoesNotExist:
            raise NotFound("Sahifa topilmadi")
        return page

    @extend_schema(
        summary="Faoliyat sahifasi tafsilotlari",
        description=(
            "Bitta faoliyat sahifasining to'liq mazmuni, "
            "bolalari va breadcrumb yo'lini qaytaradi."
        ),
        responses={200: ActivityPageDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
