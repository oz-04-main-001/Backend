# 20241023 수정
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.amenities.models import AccommodationAmenity, Amenity, Option, RoomOption
from apps.amenities.serializers.amenities_serializers import (
    AccommodationAmenitySerializer,
    AmenitySerializer,
    DetailedAccommodationAmenitySerializer,
    DetailedRoomOptionSerializer,
    OptionSerializer,
    RoomOptionSerializer,
)


# Amenity views
@extend_schema(tags=["Host"])
class AmenityListCreateView(generics.ListCreateAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        try:
            serializer.save(is_custom=True)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response({"detail": "An amenity with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
class AmenityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]

    def perform_destroy(self, instance):
        if instance.accommodationamenity_set.exists():
            raise ValidationError("Cannot delete amenity that is in use")
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# AccommodationAmenity views
@extend_schema(tags=["Host"])
class AccommodationAmenityListCreateView(generics.ListCreateAPIView):
    serializer_class = AccommodationAmenitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return AccommodationAmenity.objects.filter(accommodation_id=self.kwargs["accommodation_id"])

    def perform_create(self, serializer):
        try:
            serializer.save(accommodation_id=self.kwargs["accommodation_id"])
        except IntegrityError:
            raise ValidationError("This amenity is already added to the accommodation")

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
class AccommodationAmenityDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AccommodationAmenitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return AccommodationAmenity.objects.filter(accommodation_id=self.kwargs["accommodation_id"])

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


@extend_schema(tags=["Host"])
class DetailedAccommodationAmenityListView(generics.ListAPIView):
    serializer_class = DetailedAccommodationAmenitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        accommodation_id = self.kwargs["accommodation_id"]
        return AccommodationAmenity.objects.filter(accommodation_id=accommodation_id).select_related("amenity")


# Option views
@extend_schema(tags=["Host"])
class OptionListCreateView(generics.ListCreateAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        try:
            serializer.save(is_custom=True)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response({"detail": "An option with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
class OptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]

    def perform_destroy(self, instance):
        if instance.roomoption_set.exists():
            raise ValidationError("Cannot delete option that is in use")
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# RoomOption views
@extend_schema(tags=["Host"])
class RoomOptionListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return RoomOption.objects.filter(room_id=self.kwargs["room_id"])

    def perform_create(self, serializer):
        try:
            serializer.save(room_id=self.kwargs["room_id"])
        except IntegrityError:
            raise ValidationError("This option is already added to the room")

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
class RoomOptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoomOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return RoomOption.objects.filter(room_id=self.kwargs["room_id"])

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


@extend_schema(tags=["Host"])
class DetailedRoomOptionListView(generics.ListAPIView):
    serializer_class = DetailedRoomOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        return RoomOption.objects.filter(room_id=room_id).select_related("option")


# Custom views
@extend_schema(tags=["Host"])
class CustomAmenityListView(generics.ListAPIView):
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Amenity.objects.filter(is_custom=True)

        return Amenity.objects.filter(
            is_custom=True, accommodationamenity__accommodation__host=self.request.user
        ).distinct()


@extend_schema(tags=["Host"])
class CustomOptionListView(generics.ListAPIView):
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Option.objects.filter(is_custom=True)

        return Option.objects.filter(is_custom=True, roomoption__room__accommodation__host=self.request.user).distinct()
