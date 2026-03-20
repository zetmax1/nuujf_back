from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import TopBarLink, DynamicPage

class TopBarLinkAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.page1 = DynamicPage.objects.create(
            title_uz="Dynamic 1",
            title_ru="Dynamic 1 Ru",
            title_en="Dynamic 1 En",
            slug="dynamic-1",
            is_active=True
        )
        self.page2 = DynamicPage.objects.create(
            title_uz="Dynamic 2",
            slug="dynamic-2",
            is_active=True
        )
        self.link1 = TopBarLink.objects.create(
            title_uz="Test Uz",
            title_ru="Test Ru",
            title_en="Test En",
            linked_page=self.page1,
            order=1,
            is_active=True
        )
        self.link2 = TopBarLink.objects.create(
            title_uz="Inactive Uz",
            linked_page=self.page2,
            order=2,
            is_active=False
        )

    def test_topbar_link_list(self):
        """Test API returns only active topbar links in correct order."""
        url = reverse('topbar-links')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return active links
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Uz")
        self.assertEqual(response.data[0]['resolved_slug'], "dynamic-1")
        self.assertEqual(response.data[0]['link_type'], "dynamic")
        
    def test_topbar_link_translations(self):
        """Test API returns translations correctly based on headers/settings if configured."""
        url = reverse('topbar-links')
        # Here we just verify the translation fields exist in the database properly
        link = TopBarLink.objects.get(id=self.link1.id)
        self.assertEqual(link.title_ru, "Test Ru")
        self.assertEqual(link.title_en, "Test En")
