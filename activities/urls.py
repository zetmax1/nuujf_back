from django.urls import path
from .views import (
    ActivityCategoryListView,
    ActivityCategoryDetailView,
    ActivityPageDetailView,
)

urlpatterns = [
    path('', ActivityCategoryListView.as_view(), name='activity-category-list'),
    path('<slug:slug>/', ActivityCategoryDetailView.as_view(), name='activity-category-detail'),
    path('<slug:category_slug>/pages/<slug:page_slug>/', ActivityPageDetailView.as_view(), name='activity-page-detail'),
]
