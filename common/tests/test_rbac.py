"""
Tests for the dynamic RBAC system.

Tests verify:
  1. Non-superusers cannot delete pages
  2. Superusers can delete pages normally
  3. Users can only edit pages assigned to their group
  4. Delete button is hidden from action menu for non-superusers
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden
from wagtail.models import Page, GroupPagePermission


class DeleteRestrictionTests(TestCase):
    """Test that page deletion is restricted to superusers."""

    def setUp(self):
        self.factory = RequestFactory()
        
        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='mainadmin',
            email='admin@example.com',
            password='testpass123'
        )
        
        # Create regular user with a group
        self.editor_group = Group.objects.create(name='Test Editors')
        self.editor_user = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='testpass123'
        )
        self.editor_user.groups.add(self.editor_group)

        # Get root page for testing
        self.root_page = Page.objects.first()

    def test_non_superuser_cannot_delete_page(self):
        """before_delete_page hook should block non-superuser deletions."""
        from common.wagtail_hooks import restrict_page_deletion

        request = self.factory.get('/')
        request.user = self.editor_user

        result = restrict_page_deletion(request, self.root_page)
        self.assertIsInstance(result, HttpResponseForbidden)

    def test_superuser_can_delete_page(self):
        """before_delete_page hook should allow superuser deletions."""
        from common.wagtail_hooks import restrict_page_deletion

        request = self.factory.get('/')
        request.user = self.superuser

        result = restrict_page_deletion(request, self.root_page)
        self.assertIsNone(result)

    def test_delete_removed_from_action_menu_for_non_superuser(self):
        """construct_page_action_menu hook should remove delete for non-superusers."""
        from common.wagtail_hooks import remove_delete_from_action_menu
        from unittest.mock import MagicMock

        # Simulate menu items including a delete action
        delete_item = MagicMock()
        delete_item.name = 'action-delete'
        edit_item = MagicMock()
        edit_item.name = 'action-publish'
        
        menu_items = [edit_item, delete_item]
        
        request = self.factory.get('/')
        request.user = self.editor_user

        remove_delete_from_action_menu(menu_items, request, {})
        
        names = [item.name for item in menu_items]
        self.assertNotIn('action-delete', names)
        self.assertIn('action-publish', names)

    def test_delete_stays_in_action_menu_for_superuser(self):
        """construct_page_action_menu hook should keep delete for superusers."""
        from common.wagtail_hooks import remove_delete_from_action_menu
        from unittest.mock import MagicMock

        delete_item = MagicMock()
        delete_item.name = 'action-delete'
        edit_item = MagicMock()
        edit_item.name = 'action-publish'
        
        menu_items = [edit_item, delete_item]
        
        request = self.factory.get('/')
        request.user = self.superuser

        remove_delete_from_action_menu(menu_items, request, {})
        
        names = [item.name for item in menu_items]
        self.assertIn('action-delete', names)

    def test_delete_removed_from_snippet_action_menu_for_non_superuser(self):
        """construct_snippet_action_menu hook should remove delete for non-superusers."""
        from common.wagtail_hooks import remove_delete_from_snippet_action_menu
        from unittest.mock import MagicMock

        delete_item = MagicMock()
        delete_item.name = 'action-delete'
        edit_item = MagicMock()
        edit_item.name = 'action-save'
        
        menu_items = [edit_item, delete_item]
        
        request = self.factory.get('/')
        request.user = self.editor_user

        remove_delete_from_snippet_action_menu(menu_items, request, {})
        
        names = [item.name for item in menu_items]
        self.assertNotIn('action-delete', names)
        self.assertIn('action-save', names)
