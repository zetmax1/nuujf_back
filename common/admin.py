from django.contrib import admin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import Vacancy, VacancyApplication


# ============================================
# WAGTAIL SNIPPET REGISTRATION
# ============================================

class VacancySnippetViewSet(SnippetViewSet):
    model = Vacancy
    icon = "user"
    menu_label = "Vakansiyalar"
    menu_name = "vacancies"
    menu_order = 400
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_display = ['title', 'department', 'category', 'employment_type', 'is_active', 'created_at']
    list_filter = ['category', 'employment_type', 'is_active']
    search_fields = ['title', 'department']


class VacancyApplicationSnippetViewSet(SnippetViewSet):
    model = VacancyApplication
    icon = "mail"
    menu_label = "Arizalar"
    menu_name = "vacancy_applications"
    menu_order = 401
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_display = ['full_name', 'vacancy', 'phone', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'vacancy']
    search_fields = ['full_name', 'phone', 'email']


register_snippet(VacancySnippetViewSet)
register_snippet(VacancyApplicationSnippetViewSet)


# ============================================
# DJANGO ADMIN REGISTRATION
# ============================================

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'category', 'employment_type', 'is_active', 'created_at']
    list_filter = ['category', 'employment_type', 'is_active']
    search_fields = ['title', 'department']
    list_editable = ['is_active']
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('title', 'department', 'category', 'employment_type')
        }),
        ('Ish haqi', {
            'fields': ('salary_min', 'salary_max')
        }),
        ("Batafsil", {
            'fields': ('description', 'requirements')
        }),
        ('Holat', {
            'fields': ('is_active',)
        }),
    )


@admin.register(VacancyApplication)
class VacancyApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'vacancy', 'phone', 'email', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'vacancy']
    search_fields = ['full_name', 'phone', 'email']
    list_editable = ['is_read']
    readonly_fields = ['full_name', 'phone', 'email', 'resume', 'cover_letter', 'vacancy', 'created_at']

    def has_add_permission(self, request):
        return False  # Applications are created via API only
