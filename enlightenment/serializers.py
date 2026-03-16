import re
from rest_framework import serializers
from wagtail.rich_text import expand_db_html
from .models import AchievementSection, EnlightenmentSection, Club


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


class AchievementSectionSerializer(serializers.ModelSerializer):
    """Serializer for achievement sections with rich text expansion."""
    content = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = AchievementSection
        fields = ['id', 'title', 'content', 'cover_image_url', 'order']

    def get_content(self, obj):
        request = self.context.get('request')
        return expand_rich_text(obj.content, request)

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class EnlightenmentSectionSerializer(serializers.ModelSerializer):
    """Serializer for enlightenment sections with rich text expansion."""
    content = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = EnlightenmentSection
        fields = ['id', 'title', 'content', 'cover_image_url', 'order']

    def get_content(self, obj):
        request = self.context.get('request')
        return expand_rich_text(obj.content, request)

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class ClubListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing clubs (card view)."""
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = ['id', 'name', 'slug', 'description', 'cover_image_url', 'order']

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class ClubDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for a single club page."""
    content = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            'id', 'name', 'slug', 'description',
            'content', 'cover_image_url', 'order',
        ]

    def get_content(self, obj):
        request = self.context.get('request')
        return expand_rich_text(obj.content, request)

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
