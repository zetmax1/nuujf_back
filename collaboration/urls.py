from django.urls import path
from .views import (
    CollaborationTypeListView,
    CollaborationTypeDetailView,
    PartnerOrganizationListView,
    PartnerOrganizationDetailView,
    CollaborationProjectListView,
    CollaborationProjectDetailView,
)

urlpatterns = [
    # Collaboration types
    path('', CollaborationTypeListView.as_view(), name='collaboration-type-list'),
    path('partners/', PartnerOrganizationListView.as_view(), name='partner-list'),
    path('projects/', CollaborationProjectListView.as_view(), name='collaboration-project-list'),
    path('<slug:slug>/', CollaborationTypeDetailView.as_view(), name='collaboration-type-detail'),
    path('partners/<slug:slug>/', PartnerOrganizationDetailView.as_view(), name='partner-detail'),
    path('projects/<slug:slug>/', CollaborationProjectDetailView.as_view(), name='collaboration-project-detail'),
]
