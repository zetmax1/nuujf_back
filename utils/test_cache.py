from django.test import TestCase, override_settings
from django.urls import path
from rest_framework.test import APIClient
from rest_framework.views import APIView
from rest_framework.response import Response
from config.mixins import CachedViewMixin, NoCacheMixin
from django.core.cache import cache
import uuid

# Dummy view for testing
class DummyCachedView(CachedViewMixin, APIView):
    def get(self, request, *args, **kwargs):
        return Response({"random_val": str(uuid.uuid4())})

class DummyNoCacheView(NoCacheMixin, APIView):
    def get(self, request, *args, **kwargs):
        return Response({"random_val": str(uuid.uuid4())})

urlpatterns = [
    path('test-cached/', DummyCachedView.as_view(), name='test-cached'),
    path('test-nocache/', DummyNoCacheView.as_view(), name='test-nocache'),
]

@override_settings(ROOT_URLCONF=__name__)
@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class CacheImplementationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def test_cached_view_caches_response(self):
        # First request
        response1 = self.client.get('/test-cached/')
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()

        # Second request
        response2 = self.client.get('/test-cached/')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()

        # Responses should be identical because of cache
        self.assertEqual(data1['random_val'], data2['random_val'])

    def test_nocache_view_does_not_cache(self):
        # First request
        response1 = self.client.get('/test-nocache/')
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()

        # Second request
        response2 = self.client.get('/test-nocache/')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()

        # Responses should be different because NoCacheMixin prevents caching
        self.assertNotEqual(data1['random_val'], data2['random_val'])
