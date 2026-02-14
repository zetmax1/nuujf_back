"""
Wagtail hooks for:
  1. Dynamic RBAC — restricts delete actions to superusers only
  2. Admin sidebar — adds shortcuts to News, Faculties, Departments pages
  3. Custom dashboard for non-superusers
"""

from django.http import HttpResponseForbidden
from django.urls import reverse
from django.utils.safestring import mark_safe
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.components import Component


# ============================================
# PAGE DELETE RESTRICTIONS
# ============================================

@hooks.register('before_delete_page')
def restrict_page_deletion(request, page):
    """
    Server-side guard: block page deletion for non-superusers.
    Even if someone bypasses the UI, this hook will prevent the delete.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden(
            "Sahifani o'chirish faqat bosh admin uchun ruxsat etilgan. "
            "(Page deletion is only allowed for the main admin.)"
        )


@hooks.register('construct_page_action_menu')
def remove_delete_from_action_menu(menu_items, request, context):
    """
    UI-level guard: remove the Delete button from the page action menu
    for all non-superusers.
    """
    if not request.user.is_superuser:
        menu_items[:] = [
            item for item in menu_items
            if item.name != 'action-delete'
        ]


@hooks.register('construct_page_listing_buttons')
def remove_delete_from_listing_buttons(buttons, page, user, context=None):
    """
    Remove the Delete button from the page listing (explorer) view
    for non-superusers — the "..." more dropdown in page lists.
    Uses URL-based detection to work with all translations (uz/ru/en).
    """
    if not user.is_superuser:
        buttons[:] = [
            button for button in buttons
            if '/delete/' not in getattr(button, 'url', '')
        ]


# ============================================
# SNIPPET DELETE RESTRICTIONS
# ============================================

@hooks.register('construct_snippet_action_menu')
def remove_delete_from_snippet_action_menu(menu_items, request, context):
    """
    UI-level guard: remove the Delete button from snippet action menus
    (Vacancy, Telegram Config, etc.) for non-superusers.
    """
    if not request.user.is_superuser:
        menu_items[:] = [
            item for item in menu_items
            if item.name != 'action-delete'
        ]


@hooks.register('construct_snippet_listing_buttons')
def remove_delete_from_snippet_listing(buttons, snippet, user, context=None):
    """
    Remove the Delete button from snippet listing views for non-superusers.
    Uses URL-based detection to work with all translations.
    """
    if not user.is_superuser:
        buttons[:] = [
            button for button in buttons
            if '/delete/' not in getattr(button, 'url', '')
        ]


# ============================================
# ADMIN SIDEBAR MENU ITEMS
# ============================================

def _get_page_explorer_url(page_model_class):
    """Helper: get the explorer URL for a specific page type."""
    try:
        page = page_model_class.objects.first()
        if page:
            return reverse('wagtailadmin_explore', args=[page.pk])
    except Exception:
        pass
    return reverse('wagtailadmin_explore_root')


@hooks.register('register_admin_menu_item')
def register_news_menu_item():
    from news.models import NewsIndexPage
    return MenuItem(
        'Yangiliklar',
        _get_page_explorer_url(NewsIndexPage),
        icon_name='doc-full-inverse',
        order=200,
    )


# @hooks.register('register_admin_menu_item')
# def register_announcements_menu_item():
#     """
#     Announcements live under the same NewsIndexPage as news posts,
#     so we link to the same explorer page.
#     """
#     from news.models import NewsIndexPage
#     return MenuItem(
#         "E'lonlar",
#         _get_page_explorer_url(NewsIndexPage),
#         icon_name='warning',
#         order=201,
#     )


@hooks.register('register_admin_menu_item')
def register_faculties_menu_item():
    from faculties.models import FacultyIndexPage
    return MenuItem(
        'Fakultetlar',
        _get_page_explorer_url(FacultyIndexPage),
        icon_name='group',
        order=210,
    )


@hooks.register('register_admin_menu_item')
def register_departments_menu_item():
    from faculties.models import DepartmentIndexPage
    return MenuItem(
        'Kafedralar',
        _get_page_explorer_url(DepartmentIndexPage),
        icon_name='clipboard-list',
        order=211,
    )


# ============================================
# CUSTOM DASHBOARD FOR NON-SUPERUSERS
# ============================================

class UserPagesPanel(Component):
    """
    A custom dashboard panel that shows non-superusers their assigned pages
    with prominent Edit buttons — much friendlier than hunting through menus.
    """
    name = "user_pages"
    order = 50

    def render_html(self, parent_context=None):
        from wagtail.models import GroupPagePermission

        request = parent_context.get('request') if parent_context else None
        if not request or not request.user or request.user.is_superuser:
            return ""

        user = request.user
        # Get all pages this user has edit access to via their groups
        user_groups = user.groups.all()
        page_perms = GroupPagePermission.objects.filter(
            group__in=user_groups,
            permission__codename='change_page',
        ).select_related('page')

        if not page_perms:
            return ""

        # Build page cards using Wagtail's native classes
        page_cards = []
        seen_pages = set()
        for perm in page_perms:
            page = perm.page
            if page.pk in seen_pages:
                continue
            seen_pages.add(page.pk)

            edit_url = reverse('wagtailadmin_pages:edit', args=[page.pk])
            explorer_url = reverse('wagtailadmin_explore', args=[page.pk])

            page_cards.append(f'''
                <div class="w-mb-2" style="
                    background: var(--w-color-surface-menus);
                    border: 1px solid var(--w-color-border-furniture);
                    border-radius: var(--w-border-radius-large, 8px);
                    padding: 1rem 1.25rem;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 1rem;
                    transition: border-color 0.15s ease;
                " onmouseover="this.style.borderColor='var(--w-color-primary)'"
                   onmouseout="this.style.borderColor='var(--w-color-border-furniture)'">
                    <div style="min-width: 0;">
                        <h3 class="w-label-1" style="
                            margin: 0 0 0.15rem 0;
                            color: white;
                        ">
                            {page.title}
                        </h3>
                        <span class="w-body-text-small" style="
                            color: var(--w-color-text-meta);
                        ">{page.specific_class._meta.verbose_name}</span>
                    </div>
                    <div style="display: flex; gap: 0.5rem; flex-shrink: 0;">
                        <a href="{edit_url}" class="button button-small button--icon bicolor" style="
                            text-decoration: none;
                        ">
                            <span class="icon-wrapper">
                                <svg class="icon icon-edit" aria-hidden="true">
                                    <use href="#icon-edit"></use>
                                </svg>
                            </span>
                            Tahrirlash
                        </a>
                        <a href="{explorer_url}" class="button button-small button-secondary" style="
                            text-decoration: none;
                        ">
                            Ko'rish
                        </a>
                    </div>
                </div>
            ''')

        cards_html = '\n'.join(page_cards)

        return mark_safe(f'''
            <section class="w-mb-6">
                <div class="w-panel" style="overflow: hidden;">
                    <header class="w-panel__header" style="
                        padding: 0.875rem 1.25rem;
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    ">
                        <svg class="icon icon-doc-full-inverse" aria-hidden="true" style="
                            width: 1.25em; height: 1.25em;
                            color: var(--w-color-primary);
                        ">
                            <use href="#icon-doc-full-inverse"></use>
                        </svg>
                        <h2 class="w-panel__heading w-label-1" style="margin: 4; padding-left: 5;">
                            Sizning sahifalaringiz
                        </h2>
                    </header>
                    <div class="w-panel__content" style="padding: 1.25rem;">
                        <p class="w-body-text-small w-mb-4" style="
                            color: var(--w-color-text-meta);
                            margin-top: 0;
                        ">
                            Tahrirlash uchun "Tahrirlash" tugmasini bosing
                        </p>
                        {cards_html}
                    </div>
                </div>
            </section>
        ''')


@hooks.register('construct_homepage_panels')
def add_user_pages_panel(request, panels):
    """
    Replace default panels with a user-friendly pages panel for non-superusers.
    Superusers keep the standard Wagtail dashboard.
    """
    if not request.user.is_superuser:
        panels[:] = [UserPagesPanel()]
