from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin import messages
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet
from wagtail.admin.widgets.button import Button

from .models import HemisStatistic
from .utils import fetch_and_update_hemis_stats

class HemisStatisticViewSet(SnippetViewSet):
    model = HemisStatistic
    menu_label = "Hemis Statistics"
    icon = "history"
    add_to_admin_menu = True
    list_display = ["updated_at", "students_count", "teachers_count", "efficiency", "directions_count"]

register_snippet(HemisStatisticViewSet)


def hemis_update_action(request):
    """
    Custom Wagtail Admin view to manually update statistics from HEMIS API.
    """
    try:
        fetch_and_update_hemis_stats()
        messages.success(request, _("Hemis stats updated successfully from API."))
    except Exception as e:
        messages.error(request, _(f"Error updating stats: {e}"))
    
    # Redirect back to the snippet list view
    return redirect('wagtailsnippets_hemis_hemisstatistic:list')


@hooks.register('register_admin_urls')
def register_hemis_admin_urls():
    return [
        path('hemis-statistics/update/', hemis_update_action, name='hemis_update_action'),
    ]

@hooks.register('register_snippet_listing_buttons')
def snippet_listing_buttons(snippet, user, next_url=None):
    if isinstance(snippet, HemisStatistic):
        yield Button(
            "Update from API",
            reverse('hemis_update_action'),
            icon_name='download',
            priority=10
        )
