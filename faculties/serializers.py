from rest_framework import serializers
from .models import (
    FacultyPage, FacultyDepartment, FacultyAchievement,
    DepartmentPage, DepartmentProgram, DepartmentSubject,
    DepartmentStaff, DepartmentPublication
)


class FacultyDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyDepartment
        fields = ['id', 'name', 'description', 'head_of_department']


class FacultyAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyAchievement
        fields = ['id', 'title', 'description', 'year']


class FacultyPageSerializer(serializers.ModelSerializer):
    departments = FacultyDepartmentSerializer(many=True, read_only=True)
    achievements = FacultyAchievementSerializer(many=True, read_only=True)
    
    class Meta:
        model = FacultyPage
        fields = [
            'id', 'title', 'slug', 'faculty_code', 'short_description',
            'description', 'phone', 'email', 'office_location',
            'dean_name', 'dean_title', 'dean_bio',
            'departments', 'achievements'
        ]


# ============================================
# DEPARTMENT SERIALIZERS
# ============================================

class DepartmentProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentProgram
        fields = ['id', 'program_type', 'code', 'name', 'description']


class DepartmentSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentSubject
        fields = ['id', 'name', 'level', 'credits', 'description']


class DepartmentStaffSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DepartmentStaff
        fields = ['id', 'name', 'title', 'email', 'specialization', 'bio', 'image_url']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.file.url
        return None


class DepartmentPublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentPublication
        fields = ['id', 'title', 'authors', 'year', 'journal_or_conference', 'link']


class DepartmentPageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for department listing"""
    faculty_name = serializers.CharField(source='faculty.title', read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DepartmentPage
        fields = [
            'id', 'title', 'slug', 'department_code', 'short_description',
            'faculty', 'faculty_name', 'cover_image_url', 'head_name'
        ]
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.file.url
        return None


class DepartmentPageSerializer(serializers.ModelSerializer):
    """Full serializer for department detail"""
    programs = DepartmentProgramSerializer(many=True, read_only=True)
    subjects = DepartmentSubjectSerializer(many=True, read_only=True)
    staff = DepartmentStaffSerializer(many=True, read_only=True)
    publications = DepartmentPublicationSerializer(many=True, read_only=True)
    faculty_name = serializers.CharField(source='faculty.title', read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    head_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DepartmentPage
        fields = [
            'id', 'title', 'slug', 'department_code', 'short_description', 'description',
            'faculty', 'faculty_name', 'cover_image_url', 'logo_url',
            'phone', 'email', 'office_location',
            'head_name', 'head_title', 'head_image_url', 'head_bio',
            'programs', 'subjects', 'staff', 'publications'
        ]
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.file.url
        return None
    
    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.file.url
        return None
    
    def get_head_image_url(self, obj):
        if obj.head_image:
            return obj.head_image.file.url
        return None