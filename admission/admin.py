from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import AdmissionYear, AdmissionQuota


# ============================================
# WAGTAIL SNIPPET REGISTRATION (grouped)
# ============================================

class AdmissionYearSnippetViewSet(SnippetViewSet):
    model = AdmissionYear
    icon = "date"
    menu_label = "Qabul yillari"
    menu_name = "admission-years"
    inspect_view_enabled = True
    list_display = ['title', 'badge_text', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title']
    ordering = ['order', '-title']


class AdmissionQuotaSnippetViewSet(SnippetViewSet):
    model = AdmissionQuota
    icon = "table"
    menu_label = "Qabul kvotalari"
    menu_name = "admission-quotas"
    inspect_view_enabled = True
    list_display = ['direction_name', 'year', 'language', 'grant_count', 'contract_count', 'order']
    list_filter = ['year']
    search_fields = ['direction_name']
    ordering = ['year', 'order', 'direction_name']


class AdmissionSnippetGroup(SnippetViewSetGroup):
    """Group all admission snippets under one 'Qabul' menu item."""
    items = (
        AdmissionYearSnippetViewSet,
        AdmissionQuotaSnippetViewSet,
    )
    menu_icon = "doc-full"
    menu_label = "Qabul"
    menu_name = "admission"
    menu_order = 450


register_snippet(AdmissionSnippetGroup)


# ============================================
# DJANGO ADMIN REGISTRATION
# ============================================

@admin.register(AdmissionYear)
class AdmissionYearAdmin(TabbedTranslationAdmin):
    list_display = ['title', 'badge_text', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ("O'quv yili", {
            'fields': ('title', 'badge_text')
        }),
        ("Bosh sahifa", {
            'fields': ('hero_title', 'hero_description')
        }),
        ("Sozlamalar", {
            'fields': ('apply_link', 'order', 'is_active')
        }),
    )


@admin.register(AdmissionQuota)
class AdmissionQuotaAdmin(TabbedTranslationAdmin):
    list_display = ['direction_name', 'year', 'language', 'grant_count', 'contract_count', 'order']
    list_filter = ['year']
    search_fields = ['direction_name']
    list_editable = ['order', 'grant_count', 'contract_count']
    fieldsets = (
        ("Asosiy", {
            'fields': ('year',)
        }),
        ("Ma'lumotlar", {
            'fields': ('direction_name', 'language', 'grant_count', 'contract_count')
        }),
        ("Sozlamalar", {
            'fields': ('order',)
        }),
    )
