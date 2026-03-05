from django.urls import path
from .views import AdmissionYearListView, AdmissionYearDetailView

urlpatterns = [
    path('', AdmissionYearListView.as_view(), name='admission-year-list'),
    path('<int:pk>/', AdmissionYearDetailView.as_view(), name='admission-year-detail'),
]
