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
