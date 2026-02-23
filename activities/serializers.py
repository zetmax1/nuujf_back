import re
from rest_framework import serializers
from wagtail.rich_text import expand_db_html
from .models import ActivityCategory, ActivityPage


def expand_rich_text(raw_html, request=None):
    """Expand Wagtail rich text and make image/document URLs absolute."""
    if not raw_html:
        return ''
    html = expand_db_html(raw_html)
    if request:
        def make_src_absolute(match):
            url = match.group(1)
            if url.startswith('/'):
                return f'src="{request.build_absolute_uri(url)}"'
            return match.group(0)

        def make_href_absolute(match):
            url = match.group(1)
            if url.startswith('/'):
                return f'href="{request.build_absolute_uri(url)}"'
            return match.group(0)

        html = re.sub(r'src="([^"]*)"', make_src_absolute, html)
        html = re.sub(r'href="(/documents/[^"]*)"', make_href_absolute, html)
    return html


class ActivityPageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing pages within a category or parent."""
    has_children = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = ActivityPage
        fields = ['id', 'title', 'slug', 'cover_image_url', 'order', 'has_children']

    def get_has_children(self, obj):
        return obj.children.filter(is_active=True).exists()

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class ActivityPageDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for a single page — includes content, children, breadcrumbs."""
    content = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    breadcrumbs = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    category_title = serializers.CharField(source='category.title', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

    class Meta:
        model = ActivityPage
        fields = [
            'id', 'title', 'slug', 'content',
            'cover_image_url', 'order',
            'category_title', 'category_slug',
            'children', 'breadcrumbs',
        ]

    def get_content(self, obj):
        request = self.context.get('request')
        return expand_rich_text(obj.content, request)

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('order', 'title')
        return ActivityPageListSerializer(
            children, many=True, context=self.context
        ).data

    def get_breadcrumbs(self, obj):
        return obj.get_breadcrumbs()

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class ActivityCategoryListSerializer(serializers.ModelSerializer):
    """Listing serializer for categories."""
    cover_image_url = serializers.SerializerMethodField()
    page_count = serializers.SerializerMethodField()

    class Meta:
        model = ActivityCategory
        fields = ['id', 'title', 'slug', 'icon', 'cover_image_url', 'order', 'page_count']

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_page_count(self, obj):
        return obj.pages.filter(is_active=True).count()


class ActivityCategoryDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for a category — includes description and direct child pages."""
    description = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()

    class Meta:
        model = ActivityCategory
        fields = [
            'id', 'title', 'slug', 'icon',
            'description', 'cover_image_url', 'order', 'pages',
        ]

    def get_description(self, obj):
        request = self.context.get('request')
        return expand_rich_text(obj.description, request)

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_pages(self, obj):
        """Return only direct child pages (parent=null)."""
        direct_pages = obj.pages.filter(
            is_active=True, parent__isnull=True
        ).order_by('order', 'title')
        return ActivityPageListSerializer(
            direct_pages, many=True, context=self.context
        ).data
