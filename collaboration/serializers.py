import re
from rest_framework import serializers
from wagtail.rich_text import expand_db_html
from .models import CollaborationType, PartnerOrganization, CollaborationProject


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


# ============================================
# PARTNER ORGANIZATION SERIALIZERS
# ============================================

class PartnerOrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing partners."""
    logo_url = serializers.SerializerMethodField()
    collaboration_type_title = serializers.CharField(
        source='collaboration_type.title', read_only=True
    )

    class Meta:
        model = PartnerOrganization
        fields = [
            'id', 'name', 'slug', 'country', 'website',
            'logo_url', 'collaboration_type_title', 'order',
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            url = obj.logo.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class PartnerOrganizationDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for a single partner organization."""
    logo_url = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    collaboration_type_title = serializers.CharField(
        source='collaboration_type.title', read_only=True
    )
    collaboration_type_slug = serializers.CharField(
        source='collaboration_type.slug', read_only=True
    )

    class Meta:
        model = PartnerOrganization
        fields = [
            'id', 'name', 'slug', 'country', 'website',
            'logo_url', 'description',
            'collaboration_type_title', 'collaboration_type_slug',
            'order',
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            url = obj.logo.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_description(self, obj):
        request = self.context.get('request')
        return expand_rich_text(obj.description, request)


# ============================================
# COLLABORATION PROJECT SERIALIZERS
# ============================================

class CollaborationProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing projects."""
    cover_image_url = serializers.SerializerMethodField()
    collaboration_type_title = serializers.CharField(
        source='collaboration_type.title', read_only=True
    )

    class Meta:
        model = CollaborationProject
        fields = [
            'id', 'title', 'slug', 'cover_image_url',
            'start_date', 'end_date', 'external_link',
            'collaboration_type_title', 'order',
        ]

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class CollaborationProjectDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for a single project."""
    content = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    partners = PartnerOrganizationListSerializer(many=True, read_only=True)
    collaboration_type_title = serializers.CharField(
        source='collaboration_type.title', read_only=True
    )
    collaboration_type_slug = serializers.CharField(
        source='collaboration_type.slug', read_only=True
    )

    class Meta:
        model = CollaborationProject
        fields = [
            'id', 'title', 'slug', 'content', 'cover_image_url',
            'start_date', 'end_date', 'external_link',
            'partners',
            'collaboration_type_title', 'collaboration_type_slug',
            'order',
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


# ============================================
# COLLABORATION TYPE SERIALIZERS
# ============================================

class CollaborationTypeListSerializer(serializers.ModelSerializer):
    """Listing serializer for collaboration types."""
    cover_image_url = serializers.SerializerMethodField()
    partner_count = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()

    class Meta:
        model = CollaborationType
        fields = [
            'id', 'title', 'slug', 'icon', 'cover_image_url',
            'order', 'partner_count', 'project_count',
        ]

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_partner_count(self, obj):
        return obj.partners.filter(is_active=True).count()

    def get_project_count(self, obj):
        return obj.projects.filter(is_active=True).count()


class CollaborationTypeDetailSerializer(serializers.ModelSerializer):
    """Detail serializer — includes description, partners, and projects."""
    description = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    partners = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = CollaborationType
        fields = [
            'id', 'title', 'slug', 'icon',
            'description', 'cover_image_url', 'order',
            'partners', 'projects',
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

    def get_partners(self, obj):
        active_partners = obj.partners.filter(
            is_active=True
        ).select_related('collaboration_type').order_by('order', 'name')
        return PartnerOrganizationListSerializer(
            active_partners, many=True, context=self.context
        ).data

    def get_projects(self, obj):
        active_projects = obj.projects.filter(
            is_active=True
        ).select_related('collaboration_type', 'cover_image').order_by('order', 'title')
        return CollaborationProjectListSerializer(
            active_projects, many=True, context=self.context
        ).data
