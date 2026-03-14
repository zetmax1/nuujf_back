from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import ScienceIndex, ResearchArea, ResearchDetail

# ============================================
# WAGTAIL SNIPPET REGISTRATION
# ============================================

class ScienceIndexSnippetViewSet(SnippetViewSet):
    model = ScienceIndex
    icon = "home"
    menu_label = "Asosiy ma'lumotlar"
    menu_name = "science-index"
    inspect_view_enabled = True

class ResearchAreaSnippetViewSet(SnippetViewSet):
    model = ResearchArea
    icon = "folder-open-inverse"
    menu_label = "Tadqiqot yo'nalishlari"
    menu_name = "research-areas"
    inspect_view_enabled = True
    list_display = ['title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']

class ResearchDetailSnippetViewSet(SnippetViewSet):
    model = ResearchDetail
    icon = "doc-full"
    menu_label = "Tadqiqot tafsilotlari"
    menu_name = "research-details"
    inspect_view_enabled = True
    list_display = ['area', 'subtitle']

class ScienceSnippetGroup(SnippetViewSetGroup):
    items = (
        ScienceIndexSnippetViewSet,
        ResearchAreaSnippetViewSet,
        ResearchDetailSnippetViewSet,
    )
    menu_icon = "site"
    menu_label = "Ilm-fan"
    menu_name = "science-group"
    menu_order = 500

register_snippet(ScienceSnippetGroup)


# ============================================
# DJANGO ADMIN REGISTRATION
# ============================================

@admin.register(ScienceIndex)
class ScienceIndexAdmin(TabbedTranslationAdmin):
    list_display = ['title']
    fieldsets = (
        ("Hero Section", {
            'fields': ('title', 'description', 'cover_image')
        }),
        ("Statistika", {
            'fields': ('stat1_label', 'stat1_value', 
                       'stat2_label', 'stat2_value',
                       'stat3_label', 'stat3_value',
                       'stat4_label', 'stat4_value')
        }),
    )

@admin.register(ResearchArea)
class ResearchAreaAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'slug', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    readonly_fields = ['slug']

@admin.register(ResearchDetail)
class ResearchDetailAdmin(TabbedTranslationAdmin):
    list_display = ['area', 'subtitle']
    fieldsets = (
        ("Header", {
            'fields': ('area', 'subtitle', 'main_image')
        }),
        ("Mazmun", {
            'fields': ('content',)
        }),
        ("Sidebar Statistika", {
            'fields': ('stat1_label', 'stat1_value', 
                       'stat2_label', 'stat2_value',
                       'stat3_label', 'stat3_value')
        }),
    )
