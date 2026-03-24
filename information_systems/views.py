from rest_framework import generics
from config.mixins import CachedViewMixin
from .models import InformationSystem
from .serializers import InformationSystemSerializer

class InformationSystemList(CachedViewMixin, generics.ListAPIView):
    queryset = InformationSystem.objects.all().select_related('icon')
    serializer_class = InformationSystemSerializer
