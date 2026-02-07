from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsViewSet, TelegramWebhookView

router = DefaultRouter()
router.register(r'', NewsViewSet, basename='news')

urlpatterns = [
    path('telegram-webhook/', TelegramWebhookView.as_view(), name='telegram-webhook'),
    path('', include(router.urls)),
]
