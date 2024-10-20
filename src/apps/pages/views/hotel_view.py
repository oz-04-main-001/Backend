from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from apps.accommodations.models import Accommodation
from apps.pages.serializers.hotel_serializer import HotelDetailSerializer


class HotelDetailView(RetrieveAPIView):
    serializer_class = HotelDetailSerializer
    queryset = Accommodation.objects.all()
