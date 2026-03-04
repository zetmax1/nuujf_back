from django.urls import path
from .views import AppealCreateView

urlpatterns = [
    path('submit/', AppealCreateView.as_view(), name='appeal-submit'),
]
