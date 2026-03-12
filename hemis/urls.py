from django.urls import path
from .views import HemisStatisticAPIView

urlpatterns = [
    path('statistics/', HemisStatisticAPIView.as_view(), name='hemis-statistics'),
]
