from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..models import AccommodationAmenity, Amenity, Option, RoomOption
from ..serializers.amenities_serializers import (
    AccommodationAmenitySerializer,
    AmenitySerializer,
    DetailedAccommodationAmenitySerializer,
    DetailedRoomOptionSerializer,
    OptionSerializer,
    RoomOptionSerializer,
)


@extend_schema(tags=["Host"])
class AmenityListCreateView(generics.ListCreateAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(is_custom=True)


@extend_schema(tags=["Host"])
class AccommodationAmenityListCreateView(generics.ListCreateAPIView):
    serializer_class = AccommodationAmenitySerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def get_queryset(self):
        return AccommodationAmenity.objects.filter(accommodation_id=self.kwargs["accommodation_id"])

    def perform_create(self, serializer):
        serializer.save(accommodation_id=self.kwargs["accommodation_id"])


@extend_schema(tags=["Host"])
class DetailedAccommodationAmenityListView(generics.ListAPIView):
    serializer_class = DetailedAccommodationAmenitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        accommodation_id = self.kwargs["accommodation_id"]
        return AccommodationAmenity.objects.filter(accommodation_id=accommodation_id).select_related("amenity")


@extend_schema(tags=["Host"])
class OptionListCreateView(generics.ListCreateAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(is_custom=True)


@extend_schema(tags=["Host"])
class RoomOptionListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomOptionSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def get_queryset(self):
        return RoomOption.objects.filter(room_id=self.kwargs["room_id"])

    def perform_create(self, serializer):
        serializer.save(room_id=self.kwargs["room_id"])


@extend_schema(tags=["Host"])
class DetailedRoomOptionListView(generics.ListAPIView):
    serializer_class = DetailedRoomOptionSerializer
    permission_classes = [AllowAny]  # [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        return RoomOption.objects.filter(room_id=room_id).select_related("option")


@extend_schema(tags=["Host"])
class CustomAmenityListView(generics.ListAPIView):
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def get_queryset(self):
        return Amenity.objects.filter(
            is_custom=True, accommodationamenity__accommodation__host=self.request.user
        ).distinct()


@extend_schema(tags=["Host"])
class CustomOptionListView(generics.ListAPIView):
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def get_queryset(self):
        return Option.objects.filter(is_custom=True, roomoption__room__accommodation__host=self.request.user).distinct()
