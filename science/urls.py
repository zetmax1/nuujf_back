from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScienceIndexView, ResearchAreaViewSet, ResearchDetailView

router = DefaultRouter()
router.register(r'areas', ResearchAreaViewSet)

urlpatterns = [
    path('index/', ScienceIndexView.as_view(), name='science-index'),
    path('detail/<slug:slug>/', ResearchDetailView.as_view(), name='research-detail'),
    path('', include(router.urls)),
]
