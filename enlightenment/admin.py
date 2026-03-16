from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import AchievementSection, EnlightenmentSection, Club


# ============================================
# WAGTAIL SNIPPET REGISTRATION
# ============================================

class AchievementSectionSnippetViewSet(SnippetViewSet):
    model = AchievementSection
    icon = "success"
    menu_label = "Yutuqlar"
    menu_name = "achievements"
    inspect_view_enabled = True
    list_display = ['title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    ordering = ['order', 'title']


class EnlightenmentSectionSnippetViewSet(SnippetViewSet):
    model = EnlightenmentSection
    icon = "openquote"
    menu_label = "Ma'rifat bo'limlari"
    menu_name = "enlightenment-sections"
    inspect_view_enabled = True
    list_display = ['title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    ordering = ['order', 'title']


class ClubSnippetViewSet(SnippetViewSet):
    model = Club
    icon = "group"
    menu_label = "Klublar"
    menu_name = "clubs"
    inspect_view_enabled = True
    list_display = ['name',  'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['order', 'name']


class EnlightenmentSnippetGroup(SnippetViewSetGroup):
    """Group all enlightenment snippets under one menu item."""
    items = (
        AchievementSectionSnippetViewSet,
        EnlightenmentSectionSnippetViewSet,
        ClubSnippetViewSet,
    )
    menu_icon = "snippet"
    menu_label = "Ma'rifiy muhit"
    menu_name = "enlightenment-group"
    menu_order = 360


register_snippet(EnlightenmentSnippetGroup)


# ============================================
# DJANGO ADMIN REGISTRATION
# ============================================

@admin.register(AchievementSection)
class AchievementSectionAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('title', 'cover_image')
        }),
        ("Mazmun", {
            'fields': ('content',)
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(EnlightenmentSection)
class EnlightenmentSectionAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('title', 'cover_image')
        }),
        ("Mazmun", {
            'fields': ('content',)
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(Club)
class ClubAdmin(TabbedTranslationAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['order', 'is_active']
    readonly_fields = ['slug']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'slug', 'cover_image')
        }),
        ("Qisqacha tavsif", {
            'fields': ('description',)
        }),
        ("To'liq mazmun", {
            'fields': ('content',)
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )
