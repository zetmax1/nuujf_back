from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VacancyViewSet, VacancyApplicationCreateView

router = DefaultRouter()
router.register(r'vacancies', VacancyViewSet, basename='vacancy')

urlpatterns = [
    path('vacancies/apply/', VacancyApplicationCreateView.as_view(), name='vacancy-apply'),
    path('', include(router.urls)),
]
