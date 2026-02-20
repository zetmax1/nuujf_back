import re
from rest_framework import serializers
from wagtail.rich_text import expand_db_html
from .models import NavItem, SubNavItem, DynamicPage


class DynamicPageSerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField()

    class Meta:
        model = DynamicPage
        fields = ['id', 'title', 'slug', 'body']

    def get_body(self, obj):
        """Expand Wagtail internal rich text to proper HTML with absolute URLs."""
        if obj.body:
            html = expand_db_html(obj.body)
            request = self.context.get('request')
            if request:
                def make_absolute(match):
                    url = match.group(1)
                    if url.startswith('/'):
                        return f'src="{request.build_absolute_uri(url)}"'
                    return match.group(0)
                html = re.sub(r'src="([^"]*)"', make_absolute, html)
                # Also fix href for document links
                def make_href_absolute(match):
                    url = match.group(1)
                    if url.startswith('/'):
                        return f'href="{request.build_absolute_uri(url)}"'
                    return match.group(0)
                html = re.sub(r'href="(/documents/[^"]*)"', make_href_absolute, html)
            return html
        return ''


class SubNavItemSerializer(serializers.ModelSerializer):
    link_type = serializers.CharField(read_only=True)
    resolved_page_id = serializers.CharField(read_only=True)
    resolved_slug = serializers.CharField(read_only=True)

    class Meta:
        model = SubNavItem
        fields = ['id', 'title', 'link_type', 'resolved_page_id', 'resolved_slug', 'order']


class NavItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    link_type = serializers.CharField(read_only=True)
    resolved_page_id = serializers.CharField(read_only=True)
    resolved_slug = serializers.CharField(read_only=True)

    class Meta:
        model = NavItem
        fields = ['id', 'title', 'link_type', 'resolved_page_id', 'resolved_slug', 'order', 'children']

    def get_children(self, obj):
        active_children = obj.children.filter(is_active=True).order_by('order', 'pk')
        return SubNavItemSerializer(active_children, many=True).data
