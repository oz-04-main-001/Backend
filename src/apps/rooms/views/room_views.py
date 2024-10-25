# 20241024 수정
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F, Prefetch
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accommodations.models import Accommodation
from apps.bookings.models import Booking
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType
from apps.rooms.serializers.room_serializer import (
    RoomImageSerializer,
    RoomInventorySerializer,
    RoomSerializer,
    RoomTypeSerializer,
    RoomUpdateSerializer,
)

User = get_user_model()


class BaseRoomView:
    """기본 Room 뷰"""

    permission_classes = [AllowAny]


class RoomListCreateView(BaseRoomView, generics.ListCreateAPIView):
    """Room 목록 조회 및 생성"""

    queryset = Room.objects.all().select_related("roomtype").prefetch_related("images")
    serializer_class = RoomSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RoomRetrieveUpdateDestroyView(BaseRoomView, generics.RetrieveUpdateDestroyAPIView):
    """Room 상세 조회, 수정, 삭제"""

    queryset = Room.objects.all().select_related("roomtype").prefetch_related("images")

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return RoomUpdateSerializer
        return RoomSerializer

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomTypeView(BaseRoomView, generics.RetrieveUpdateAPIView):
    """Room 타입 조회 및 수정"""

    serializer_class = RoomTypeSerializer

    def get_queryset(self):
        return RoomType.objects.filter(room_id=self.kwargs["room_id"])

    def get_object(self):
        room = get_object_or_404(Room, id=self.kwargs["room_id"])
        return room.roomtype

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class RoomImageView(BaseRoomView, generics.ListCreateAPIView, generics.DestroyAPIView):
    """Room 이미지 관리"""

    serializer_class = RoomImageSerializer

    def get_queryset(self):
        return Room_Image.objects.filter(room_id=self.kwargs["room_id"])

    def get_object(self):
        return get_object_or_404(Room, pk=self.kwargs["room_id"])

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        room = self.get_object()

        if "images" not in request.FILES:
            raise ValidationError({"images": "이미지 파일은 필수입니다."})

        images = request.FILES.getlist("images")
        total_size = sum(image.size for image in images)

        if total_size > 50 * 1024 * 1024:  # 50MB
            raise ValidationError({"images": "전체 이미지 크기가 50MB를 초과할 수 없습니다."})

        # 기존 이미지 삭제 여부 확인
        if request.data.get("delete_existing", "").lower() == "true":
            room.images.all().delete()

        image_instances = []
        for image in images:
            serializer = RoomImageSerializer(data={"image": image})
            if serializer.is_valid(raise_exception=True):
                image_instances.append(Room_Image(room=room, image=image))

        created_images = Room_Image.objects.bulk_create(image_instances)
        serializer = self.get_serializer(created_images, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        room = self.get_object()
        room.images.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomInventoryView(BaseRoomView, generics.RetrieveUpdateAPIView):
    """Room 인벤토리 조회 및 수정"""

    serializer_class = RoomInventorySerializer

    def get_queryset(self):
        return RoomInventory.objects.filter(room_id=self.kwargs["room_id"])

    def get_object(self):
        room = get_object_or_404(Room, id=self.kwargs["room_id"])
        return room.roominventory

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
