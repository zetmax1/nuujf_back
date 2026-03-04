from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import Leader, StructureSection, SectionMember


# ============================================
# WAGTAIL SNIPPET REGISTRATION
# ============================================

class LeaderSnippetViewSet(SnippetViewSet):
    model = Leader
    icon = "user"
    menu_label = "Rahbariyat"
    menu_name = "leaders"
    menu_order = 300
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_display = ['full_name', 'position', 'email', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['full_name', 'position']
    ordering = ['order', 'full_name']


register_snippet(LeaderSnippetViewSet)


class StructureSectionSnippetViewSet(SnippetViewSet):
    model = StructureSection
    icon = "list-ul"
    menu_label = "Tuzilma"
    menu_name = "structure"
    menu_order = 310
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_display = ['name', 'parent', 'leader', 'order', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    ordering = ['order', 'name']


register_snippet(StructureSectionSnippetViewSet)


# ============================================
# DJANGO ADMIN REGISTRATION
# ============================================

@admin.register(Leader)
class LeaderAdmin(TabbedTranslationAdmin):
    list_display = ['full_name', 'position', 'email', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['full_name', 'position']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('full_name', 'position', 'academic_degree', 'image')
        }),
        ("Aloqa ma'lumotlari", {
            'fields': ('email', 'phone', 'reception_days')
        }),
        ("Biografiya", {
            'fields': ('bio',)
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )


class SectionMemberInline(TranslationTabularInline):
    model = SectionMember
    extra = 1
    fields = ['full_name', 'position', 'email', 'phone', 'image', 'order']
    ordering = ['order', 'full_name']


@admin.register(StructureSection)
class StructureSectionAdmin(TabbedTranslationAdmin):
    list_display = ['name', 'parent', 'leader', 'order', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SectionMemberInline]
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'slug', 'icon', 'parent', 'leader')
        }),
        ("Tavsif", {
            'fields': ('description',)
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )
