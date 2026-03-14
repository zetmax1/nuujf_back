from rest_framework import viewsets, generics, pagination
from .models import ScienceIndex, ResearchArea, ResearchDetail
from .serializers import ScienceIndexSerializer, ResearchAreaSerializer, ResearchDetailSerializer

class ScienceIndexView(generics.RetrieveAPIView):
    queryset = ScienceIndex.objects.all()
    serializer_class = ScienceIndexSerializer

    def get_object(self):
        return ScienceIndex.objects.first()

class SciencePagination(pagination.PageNumberPagination):
    page_size = 12

class ResearchAreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchArea.objects.filter(is_active=True)
    serializer_class = ResearchAreaSerializer
    pagination_class = SciencePagination
    lookup_field = 'slug'

class ResearchDetailView(generics.RetrieveAPIView):
    queryset = ResearchArea.objects.filter(is_active=True)
    serializer_class = ResearchAreaSerializer
    lookup_field = 'slug'
