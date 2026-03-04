from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from drf_spectacular.utils import extend_schema
from .models import Appeal
from .serializers import AppealCreateSerializer


# ============================================
# SECURITY: Custom throttle classes
# ============================================

class AppealBurstThrottle(AnonRateThrottle):
    """Limit rapid-fire submissions: max 3 per minute per IP"""
    rate = '3/min'
    scope = 'appeal_burst'


class AppealDailyThrottle(AnonRateThrottle):
    """Limit total daily submissions: max 10 per day per IP"""
    rate = '10/day'
    scope = 'appeal_daily'


@extend_schema(tags=['Appeals'])
class AppealCreateView(generics.CreateAPIView):
    """
    Submit a public appeal to the university director.

    No authentication required — public form submission.
    Security measures:
    - Rate limiting: 3 requests/min, 10 requests/day per IP
    - Input sanitization: HTML stripping, length limits
    - Phone number format validation
    - Terms of use acceptance required
    """
    serializer_class = AppealCreateSerializer
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AppealBurstThrottle, AppealDailyThrottle]

    @extend_schema(
        summary="Direktoga murojaat yuborish",
        description=(
            "Universitet direktoriga ochiq murojaat yuborish. "
            "Tezlik cheklovi: daqiqasiga 3 ta, kuniga 10 ta murojaat."
        ),
        responses={201: AppealCreateSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appeal = serializer.save()
        return Response(
            {
                'status': 'success',
                'message': "Murojaatingiz muvaffaqiyatli yuborildi! Tez orada ko'rib chiqiladi.",
                'appeal': AppealCreateSerializer(appeal).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def throttled(self, request, wait):
        """Custom throttle error message in Uzbek"""
        from rest_framework.exceptions import Throttled
        raise Throttled(
            detail={
                'message': "Juda ko'p murojaat yubordingiz. Iltimos, biroz kuting.",
                'wait_seconds': int(wait),
            }
        )
