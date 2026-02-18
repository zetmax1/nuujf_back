from django.urls import path
from .views import LeaderListView, StructureTreeView, StructureSectionDetailView

urlpatterns = [
    path('leaders/', LeaderListView.as_view(), name='leader-list'),
    path('structure/', StructureTreeView.as_view(), name='structure-tree'),
    path('structure/<slug:slug>/', StructureSectionDetailView.as_view(), name='structure-detail'),
]
