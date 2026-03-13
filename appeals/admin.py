from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import Appeal


# ============================================
# WAGTAIL SNIPPET REGISTRATION
# ============================================

class AppealSnippetViewSet(SnippetViewSet):
    model = Appeal
    icon = "mail"
    menu_label = "Direktorga murojaatlar"
    menu_name = "appeals"
    menu_order = 500
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_display = ['full_name', 'email', 'department', 'phone', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'message']
    ordering = ['-created_at']


register_snippet(AppealSnippetViewSet)


# ============================================
# DJANGO ADMIN REGISTRATION
# ============================================

@admin.register(Appeal)
class AppealAdmin(TabbedTranslationAdmin):
    list_display = ['full_name', 'email', 'department', 'phone', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'message']
    list_editable = ['is_read']
    readonly_fields = ['full_name', 'email', 'department', 'phone', 'group_number', 'message', 'terms_accepted', 'created_at']
    fieldsets = (
        ("Murojaat yuboruvchi", {
            'fields': ('full_name', 'email', 'department', 'group_number', 'phone')
        }),
        ("Murojaat matni", {
            'fields': ('message',)
        }),
        ("Holat", {
            'fields': ('terms_accepted', 'is_read', 'created_at')
        }),
    )

    def has_add_permission(self, request):
        return False  # Appeals are created via API only
