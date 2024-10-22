from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F, Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Accommodation, Room, Room_Image, RoomInventory, RoomType
from ..serializers.room_serializer import (
    RoomImageSerializer,
    RoomInventorySerializer,
    RoomSerializer,
    RoomTypeSerializer,
)

User = get_user_model()


@extend_schema(tags=["Host"])
class AccommodationRoomsView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["is_available", "capacity"]
    ordering_fields = ["price", "created_at"]

    def get_queryset(self):
        accommodation_id = self.kwargs["accommodation_id"]
        return Room.objects.filter(accommodation_id=accommodation_id)


@extend_schema(tags=["Host"])
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        """

        Perform_create method is responsible for creating a new room object and associated room inventory.
        It first retrieves the accommodation id from the request data and fetches the corresponding accommodation object.
        Next, it checks if there is a business user (a user with is_superuser set to True) available, and if not, raises a ValidationError.
        Then, it verifies that the authenticated user has permission to add rooms to the accommodation by comparing the host_id of the accommodation with the business user's id.

        If the permission check passes, the method saves the room object using the serializer and creates a new RoomInventory object for this room.
        If the room does not exist in the Room model, a new RoomInventory object is created with count_room set to 1. If the room already exists, the count_room is incremented by 1.

        """
        accommodation_id = self.request.data.get("accommodation")
        accommodation = get_object_or_404(Accommodation, id=accommodation_id)

        # 슈퍼유저를 비즈니스유저로 간주
        business_user = User.objects.filter(is_superuser=True).first()

        if not business_user:
            raise ValidationError("No business user available.")

        if accommodation.host_id != business_user.id:
            raise ValidationError("You don't have permission to add rooms to this accommodation.")

        room = serializer.save()
        if not Room.objects.filter(id=room.id).exists():
            RoomInventory.objects.create(room=room, count_room=1)
        RoomInventory.objects.filter(room=room).update(count_room=F("count_room") + 1)


@extend_schema(tags=["Host"])
class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def perform_destroy(self, instance):
        inventory = instance.roominventory
        inventory.count_room -= 1
        if inventory.count_room <= 0:
            inventory.delete()
        else:
            inventory.save()
        instance.delete()


@extend_schema(tags=["Host"])
class RoomImageCreateView(generics.CreateAPIView):
    serializer_class = RoomImageSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def perform_create(self, serializer):
        room = get_object_or_404(Room, pk=self.kwargs["pk"])
        serializer.save(room=room)


@extend_schema(tags=["Host"])
class RoomTypeListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomTypeSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def get_queryset(self):
        return RoomType.objects.filter(is_customized=False) | RoomType.objects.filter(
            room__accommodation__host=self.request.user, is_customized=True
        )


@extend_schema(tags=["Host"])
class RoomTypeCustomCreateView(generics.CreateAPIView):
    serializer_class = RoomTypeSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(is_customized=True)


@extend_schema(tags=["Host"])
class RoomInventoryUpdateView(generics.UpdateAPIView):
    queryset = RoomInventory.objects.all()
    serializer_class = RoomInventorySerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.count_room <= 0:
            instance.delete()
