import re
from rest_framework import serializers
from wagtail.rich_text import expand_db_html
from .models import (
    Faculty, FacultyAchievement,
    Department, DepartmentProgram, DepartmentSubject,
    DepartmentStaff, DepartmentPublication,
)


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


def get_image_url(image, request=None) -> str | None:
    """Return absolute URL for a Wagtail image."""
    if not image:
        return None
    url = image.file.url
    if request:
        return request.build_absolute_uri(url)
    return url


# ============================================
# FACULTY SERIALIZERS
# ============================================

class FacultyAchievementSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = FacultyAchievement
        fields = ['id', 'title', 'description', 'year', 'link', 'image_url']

    def get_image_url(self, obj) -> str | None:
        return get_image_url(obj.image, self.context.get('request'))


class FacultyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for faculty listing."""
    cover_image_url = serializers.SerializerMethodField()
    departments_count = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = [
            'id', 'name', 'slug', 'faculty_code',
            'short_description', 'cover_image_url',
            'dean_name', 'departments_count',
        ]

    def get_cover_image_url(self, obj) -> str | None:
        return get_image_url(obj.cover_image, self.context.get('request'))

    def get_departments_count(self, obj) -> int:
        if hasattr(obj, 'active_departments_count'):
            return obj.active_departments_count
        return obj.departments.filter(is_active=True).count()


class FacultyDetailSerializer(serializers.ModelSerializer):
    """Full serializer for faculty detail — includes nested departments & achievements."""
    description = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    dean_image_url = serializers.SerializerMethodField()
    achievements = FacultyAchievementSerializer(many=True, read_only=True)
    departments = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = [
            'id', 'name', 'slug', 'faculty_code',
            'short_description', 'description',
            'cover_image_url',
            'phone', 'email', 'office_location',
            'dean_name', 'dean_image_url',
            'departments', 'achievements',
        ]

    def get_description(self, obj) -> str:
        return expand_rich_text(obj.description, self.context.get('request'))

    def get_cover_image_url(self, obj) -> str | None:
        return get_image_url(obj.cover_image, self.context.get('request'))

    def get_dean_image_url(self, obj) -> str | None:
        return get_image_url(obj.dean_image, self.context.get('request'))

    def get_departments(self, obj) -> list:
        """Nested departments belonging to this faculty."""
        departments = obj.departments.filter(is_active=True).order_by('order', 'name')
        return DepartmentListSerializer(
            departments, many=True, context=self.context
        ).data


# ============================================
# DEPARTMENT SERIALIZERS
# ============================================

class DepartmentProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentProgram
        fields = ['id', 'code', 'name', 'degree']


class DepartmentSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentSubject
        fields = ['id', 'name', 'description']


class DepartmentStaffSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = DepartmentStaff
        fields = ['id', 'name', 'email', 'image_url']

    def get_image_url(self, obj) -> str | None:
        return get_image_url(obj.image, self.context.get('request'))


class DepartmentPublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentPublication
        fields = ['id', 'title', 'authors', 'year', 'journal_or_conference', 'link']


class DepartmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for department listing."""
    faculty_name = serializers.CharField(source='faculty.name', default=None, read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'slug', 'department_code',
            'short_description', 'faculty', 'faculty_name',
            'cover_image_url', 'head_name',
        ]

    def get_cover_image_url(self, obj) -> str | None:
        return get_image_url(obj.cover_image, self.context.get('request'))


class DepartmentDetailSerializer(serializers.ModelSerializer):
    """Full serializer — returns ALL related data in one API call."""
    description = serializers.SerializerMethodField()
    faculty_name = serializers.CharField(source='faculty.name', default=None, read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    head_image_url = serializers.SerializerMethodField()
    programs = DepartmentProgramSerializer(many=True, read_only=True)
    subjects = DepartmentSubjectSerializer(many=True, read_only=True)
    staff = DepartmentStaffSerializer(many=True, read_only=True)
    publications = DepartmentPublicationSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'slug', 'department_code',
            'short_description', 'description',
            'faculty', 'faculty_name',
            'cover_image_url',
            'phone', 'email', 'office_location', 'reception_time',
            'head_name', 'head_image_url',
            'programs', 'subjects', 'staff', 'publications',
        ]

    def get_description(self, obj) -> str:
        return expand_rich_text(obj.description, self.context.get('request'))

    def get_cover_image_url(self, obj) -> str | None:
        return get_image_url(obj.cover_image, self.context.get('request'))

    def get_head_image_url(self, obj) -> str | None:
        return get_image_url(obj.head_image, self.context.get('request'))