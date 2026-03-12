from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HemisStatistic
from .serializers import HemisStatisticSerializer

class HemisStatisticAPIView(APIView):
    """
    Returns the statics data retrieved from HEMIS and saved locally.
    """
    def get(self, request, *args, **kwargs):
        stats = HemisStatistic.load()
        serializer = HemisStatisticSerializer(stats)
        return Response(serializer.data)

