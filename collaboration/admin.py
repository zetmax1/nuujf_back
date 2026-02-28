from django.contrib import admin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import CollaborationType, PartnerOrganization, CollaborationProject, CollaborationPage


# ============================================
# WAGTAIL SNIPPET REGISTRATION (grouped)
# ============================================

class CollaborationTypeSnippetViewSet(SnippetViewSet):
    model = CollaborationType
    icon = "globe"
    menu_label = "Hamkorlik turlari"
    menu_name = "collaboration-types"
    inspect_view_enabled = True
    list_display = ['title', 'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    ordering = ['order', 'title']


class PartnerOrganizationSnippetViewSet(SnippetViewSet):
    model = PartnerOrganization
    icon = "group"
    menu_label = "Hamkor tashkilotlar"
    menu_name = "partner-organizations"
    inspect_view_enabled = True
    list_display = ['name', 'country', 'collaboration_type', 'order', 'is_active']
    list_filter = ['is_active', 'collaboration_type', 'country']
    search_fields = ['name', 'country']
    ordering = ['order', 'name']


class CollaborationProjectSnippetViewSet(SnippetViewSet):
    model = CollaborationProject
    icon = "doc-full"
    menu_label = "Hamkorlik loyihalari"
    menu_name = "collaboration-projects"
    inspect_view_enabled = True
    list_display = ['title', 'collaboration_type', 'start_date', 'end_date', 'order', 'is_active']
    list_filter = ['is_active', 'collaboration_type']
    search_fields = ['title']
    ordering = ['order', 'title']


class CollaborationPageSnippetViewSet(SnippetViewSet):
    model = CollaborationPage
    icon = "doc-full-inverse"
    menu_label = "Hamkorlik sahifalari"
    menu_name = "collaboration-pages"
    inspect_view_enabled = True
    list_display = ['title', 'collaboration_type', 'parent', 'order', 'is_active']
    list_filter = ['is_active', 'collaboration_type']
    search_fields = ['title']
    ordering = ['collaboration_type', 'order', 'title']


class CollaborationSnippetGroup(SnippetViewSetGroup):
    """Group all collaboration snippets under one 'Hamkorlik' menu item."""
    items = (
        CollaborationTypeSnippetViewSet,
        PartnerOrganizationSnippetViewSet,
        CollaborationProjectSnippetViewSet,
        CollaborationPageSnippetViewSet,
    )
    menu_icon = "globe"
    menu_label = "Hamkorlik"
    menu_name = "collaboration"
    menu_order = 400


register_snippet(CollaborationSnippetGroup)


# ============================================
# DJANGO ADMIN REGISTRATION
# ============================================

@admin.register(CollaborationType)
class CollaborationTypeAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    readonly_fields = ['slug']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('title', 'slug', 'icon', 'cover_image')
        }),
        ("Tavsif", {
            'fields': ('description',)
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(PartnerOrganization)
class PartnerOrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'collaboration_type', 'slug', 'order', 'is_active']
    list_filter = ['is_active', 'collaboration_type', 'country']
    search_fields = ['name', 'country']
    list_editable = ['order', 'is_active']
    readonly_fields = ['slug']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'slug', 'collaboration_type', 'country', 'website', 'logo', 'cover_image')
        }),
        ("Tavsif", {
            'fields': ('description',)
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(CollaborationProject)
class CollaborationProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'collaboration_type', 'start_date', 'end_date', 'slug', 'order', 'is_active']
    list_filter = ['is_active', 'collaboration_type']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    readonly_fields = ['slug']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('title', 'slug', 'collaboration_type', 'cover_image')
        }),
        ("Mazmun", {
            'fields': ('content',)
        }),
        ("Qo'shimcha", {
            'fields': ('start_date', 'end_date', 'external_link', 'partners')
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )
    filter_horizontal = ['partners']


@admin.register(CollaborationPage)
class CollaborationPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'collaboration_type', 'parent', 'slug', 'order', 'is_active']
    list_filter = ['is_active', 'collaboration_type']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    readonly_fields = ['slug']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('title', 'slug', 'collaboration_type', 'parent', 'cover_image')
        }),
        ("Mazmun", {
            'fields': ('content',)
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )
