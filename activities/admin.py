from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import ActivityCategory, ActivityPage


# ============================================
# WAGTAIL SNIPPET REGISTRATION
# ============================================

class ActivityCategorySnippetViewSet(SnippetViewSet):
    model = ActivityCategory
    icon = "doc-full"
    menu_label = "Faoliyatlar"
    menu_name = "activities"
    inspect_view_enabled = True
    list_display = ['title', 'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    ordering = ['order', 'title']


class ActivityPageSnippetViewSet(SnippetViewSet):
    model = ActivityPage
    icon = "doc-full-inverse"
    menu_label = "Faoliyat sahifalari"
    menu_name = "activity-pages"
    inspect_view_enabled = True
    list_display = ['title', 'category', 'parent', 'order', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['title']
    ordering = ['category__order', 'order', 'title']


class ActivitySnippetGroup(SnippetViewSetGroup):
    """Group all activity snippets under one 'Faoliyat' menu item."""
    items = (
        ActivityCategorySnippetViewSet,
        ActivityPageSnippetViewSet,
    )
    menu_icon = "doc-full"
    menu_label = "Faoliyat"
    menu_name = "activities-group"
    menu_order = 350


register_snippet(ActivitySnippetGroup)


# ============================================
# DJANGO ADMIN REGISTRATION
# ============================================

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(TabbedTranslationAdmin):
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


@admin.register(ActivityPage)
class ActivityPageAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'category', 'parent', 'slug', 'order', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    readonly_fields = ['slug']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('title', 'slug', 'category', 'parent', 'cover_image')
        }),
        ("Mazmun", {
            'fields': ('content',)
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )
