from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView

from apps.pages.serializers.booking_request_serializer import BookingRequestSerializer
from apps.rooms.models import Room


@extend_schema(tags=["Guest"])
class BookingRequestView(RetrieveAPIView):
    serializer_class = BookingRequestSerializer

    def get_queryset(self):
        hotel_pk = self.kwargs["hotel_pk"]
        return Room.objects.filter(accommodation__id=hotel_pk)

    @extend_schema(
        summary=">> 예약 요청 /{숙소_id}/{룸_id}/ <<",
        description="capacity:기준인원 / ",
        responses={200: BookingRequestSerializer()},  # 응답이 리스트 형태로 나타남
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
