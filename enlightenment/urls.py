from django.urls import path
from .views import (
    AchievementSectionListView,
    EnlightenmentSectionListView,
    ClubListView,
    ClubDetailView,
    StatsView,
)

urlpatterns = [
    path('achievements/', AchievementSectionListView.as_view(), name='achievement-section-list'),
    path('sections/', EnlightenmentSectionListView.as_view(), name='enlightenment-section-list'),
    path('clubs/', ClubListView.as_view(), name='club-list'),
    path('clubs/<slug:slug>/', ClubDetailView.as_view(), name='club-detail'),
    path('stats/', StatsView.as_view(), name='enlightenment-stats'),
]
