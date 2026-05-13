from django.urls import path
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .views import ClearCacheView


@hooks.register('register_admin_urls')
def register_cache_clear_url():
    return [
        path('clear-cache/', ClearCacheView.as_view(), name='clear_cache'),
    ]


@hooks.register('register_admin_menu_item')
def register_cache_clear_menu_item():
    return MenuItem(
        'Clear cache',        # Label shown in the sidebar
        '/admin/clear-cache/',    # The Wagtail admin URL prefix is /admin/
        icon_name='bin',
        order=10000,              # Push to the very bottom of the sidebar
    )
