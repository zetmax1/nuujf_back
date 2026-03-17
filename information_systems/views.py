from rest_framework import generics
from .models import InformationSystem
from .serializers import InformationSystemSerializer

class InformationSystemList(generics.ListAPIView):
    queryset = InformationSystem.objects.all()
    serializer_class = InformationSystemSerializer
