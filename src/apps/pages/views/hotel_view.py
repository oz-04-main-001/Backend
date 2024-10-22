from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from apps.accommodations.models import Accommodation
from apps.pages.serializers.hotel_serializer import HotelDetailSerializer


@extend_schema(tags=["Guest"])
class HotelDetailView(RetrieveAPIView):
    serializer_class = HotelDetailSerializer
    queryset = Accommodation.objects.all()
