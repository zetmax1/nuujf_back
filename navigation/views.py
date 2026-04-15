from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.exceptions import NotFound
from config.mixins import CachedViewMixin
from .models import NavItem, DynamicPage, TopBarLink
from .serializers import NavItemSerializer, DynamicPageSerializer, TopBarLinkSerializer


class NavItemListView(CachedViewMixin, ListAPIView):
    """Returns the full navigation tree for the frontend navbar."""
    serializer_class = NavItemSerializer
    pagination_class = None

    def get_queryset(self):
        return NavItem.objects.filter(
            is_active=True
        ).prefetch_related(
            'children', 'linked_page', 'children__linked_page',
            'linked_activity_category', 'children__linked_activity_category'
        ).order_by('order', 'pk')


class DynamicPageDetailView(CachedViewMixin, RetrieveAPIView):
    """Returns the content of a dynamic page by its slug."""
    serializer_class = DynamicPageSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return DynamicPage.objects.filter(is_active=True)

    def get_object(self):
        slug = self.kwargs['slug']
        if slug in ('null', 'undefined'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Noto'g'ri slug kiritildi (null or undefined)")
            
        try:
            return self.get_queryset().get(slug=slug)
        except DynamicPage.DoesNotExist:
            raise NotFound("Sahifa topilmadi")


class TopBarLinkListView(CachedViewMixin, ListAPIView):
    """Returns the list of active top bar links."""
    serializer_class = TopBarLinkSerializer
    pagination_class = None

    def get_queryset(self):
        return TopBarLink.objects.filter(is_active=True).select_related('linked_page').order_by('order', 'pk')
