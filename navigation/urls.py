from django.urls import path
from .views import NavItemListView, DynamicPageDetailView, TopBarLinkListView

urlpatterns = [
    path('items/', NavItemListView.as_view(), name='nav-items'),
    path('pages/<slug:slug>/', DynamicPageDetailView.as_view(), name='dynamic-page-detail'),
    path('topbar/', TopBarLinkListView.as_view(), name='topbar-links'),
]
