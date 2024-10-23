from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView

from apps.bookings.models import Booking
from apps.pages.serializers.booking_status_serializer import BookingStatusSerializer


@extend_schema(tags=["Guest"])
class BookingStatusView(RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingStatusSerializer

    @extend_schema(
        summary=">> 예약 상태 확인 /{booking_id}/ <<",
        description="예약 상태 확인",
        responses={200: BookingStatusSerializer()},  # 응답이 리스트 형태로 나타남
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
