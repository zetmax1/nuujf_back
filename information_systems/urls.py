from django.urls import path
from .views import InformationSystemList

urlpatterns = [
    path('', InformationSystemList.as_view(), name='information-systems-list'),
]
