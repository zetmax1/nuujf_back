from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import (
    Faculty, FacultyAchievement,
    Department, DepartmentProgram, DepartmentSubject,
    DepartmentStaff, DepartmentPublication,
)


# ============================================
# WAGTAIL SNIPPET REGISTRATION
# ============================================

class FacultySnippetViewSet(SnippetViewSet):
    model = Faculty
    icon = "group"
    menu_label = "Fakultetlar"
    menu_name = "faculties"
    inspect_view_enabled = True
    list_display = ['name', 'faculty_code', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'faculty_code']
    ordering = ['order', 'name']


class FacultyAchievementSnippetViewSet(SnippetViewSet):
    model = FacultyAchievement
    icon = "success"
    menu_label = "Yutuqlar"
    menu_name = "faculty-achievements"
    inspect_view_enabled = True
    list_display = ['title', 'faculty', 'year']
    list_filter = ['faculty']
    search_fields = ['title']
    ordering = ['-year']


class DepartmentSnippetViewSet(SnippetViewSet):
    model = Department
    icon = "clipboard-list"
    menu_label = "Kafedralar"
    menu_name = "departments"
    inspect_view_enabled = True
    list_display = ['name', 'department_code', 'faculty', 'order', 'is_active']
    list_filter = ['is_active', 'faculty']
    search_fields = ['name', 'department_code']
    ordering = ['order', 'name']


class DepartmentProgramSnippetViewSet(SnippetViewSet):
    model = DepartmentProgram
    icon = "doc-full"
    menu_label = "Dasturlar"
    menu_name = "department-programs"
    inspect_view_enabled = True
    list_display = ['name', 'code', 'department']
    list_filter = ['department']
    search_fields = ['name', 'code']


class DepartmentSubjectSnippetViewSet(SnippetViewSet):
    model = DepartmentSubject
    icon = "list-ul"
    menu_label = "Fanlar"
    menu_name = "department-subjects"
    inspect_view_enabled = True
    list_display = ['name', 'department']
    list_filter = ['department']
    search_fields = ['name']


class DepartmentStaffSnippetViewSet(SnippetViewSet):
    model = DepartmentStaff
    icon = "user"
    menu_label = "Xodimlar"
    menu_name = "department-staff"
    inspect_view_enabled = True
    list_display = ['name', 'email', 'department']
    list_filter = ['department']
    search_fields = ['name']


class DepartmentPublicationSnippetViewSet(SnippetViewSet):
    model = DepartmentPublication
    icon = "doc-full-inverse"
    menu_label = "Nashrlar"
    menu_name = "department-publications"
    inspect_view_enabled = True
    list_display = ['title', 'authors', 'year', 'department']
    list_filter = ['department', 'year']
    search_fields = ['title', 'authors']
    ordering = ['-year']


class FacultiesSnippetGroup(SnippetViewSetGroup):
    """Group all faculty/department snippets under one menu item."""
    items = (
        FacultySnippetViewSet,
        FacultyAchievementSnippetViewSet,
        DepartmentSnippetViewSet,
        DepartmentProgramSnippetViewSet,
        DepartmentSubjectSnippetViewSet,
        DepartmentStaffSnippetViewSet,
        DepartmentPublicationSnippetViewSet,
    )
    menu_icon = "group"
    menu_label = "Fakultet va Kafedralar"
    menu_name = "faculties-group"
    menu_order = 210


register_snippet(FacultiesSnippetGroup)


# ============================================
# DJANGO ADMIN REGISTRATION
# ============================================

class FacultyAchievementInline(TranslationTabularInline):
    model = FacultyAchievement
    extra = 0


@admin.register(Faculty)
class FacultyAdmin(TabbedTranslationAdmin):
    list_display = ['name', 'faculty_code', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'faculty_code']
    list_editable = ['order', 'is_active']
    readonly_fields = ['slug']
    inlines = [FacultyAchievementInline]
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'slug', 'faculty_code', 'cover_image')
        }),
        ("Qisqacha tavsif", {
            'fields': ('short_description',)
        }),
        ("To'liq tavsif", {
            'fields': ('description',)
        }),
        ("Dekan ma'lumotlari", {
            'fields': ('dean_name', 'dean_image')
        }),
        ("Aloqa", {
            'fields': ('phone', 'email', 'office_location')
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )


class DepartmentProgramInline(TranslationTabularInline):
    model = DepartmentProgram
    extra = 0


class DepartmentSubjectInline(TranslationTabularInline):
    model = DepartmentSubject
    extra = 0


class DepartmentStaffInline(TranslationTabularInline):
    model = DepartmentStaff
    extra = 0


class DepartmentPublicationInline(TranslationTabularInline):
    model = DepartmentPublication
    extra = 0


@admin.register(Department)
class DepartmentAdmin(TabbedTranslationAdmin):
    list_display = ['name', 'department_code', 'faculty', 'order', 'is_active']
    list_filter = ['is_active', 'faculty']
    search_fields = ['name', 'department_code']
    list_editable = ['order', 'is_active']
    readonly_fields = ['slug']
    inlines = [DepartmentProgramInline, DepartmentSubjectInline, DepartmentStaffInline, DepartmentPublicationInline]
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'slug', 'department_code', 'faculty', 'cover_image')
        }),
        ("Qisqacha tavsif", {
            'fields': ('short_description',)
        }),
        ("To'liq tavsif", {
            'fields': ('description',)
        }),
        ("Kafedra mudiri", {
            'fields': ('head_name', 'head_image')
        }),
        ("Aloqa", {
            'fields': ('phone', 'email', 'office_location')
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )
