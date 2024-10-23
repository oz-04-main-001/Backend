# 20241023 수정
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
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType
from apps.rooms.serializers.room_serializer import (
    RoomImageSerializer,
    RoomInventorySerializer,
    RoomSerializer,
    RoomTypeSerializer,
)

User = get_user_model()


@extend_schema(tags=["Host"])
class AccommodationRoomsView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["is_available", "capacity"]
    ordering_fields = ["price", "created_at"]

    def get_queryset(self):
        accommodation_id = self.kwargs.get("accommodation_id")

        # Validate accommodation exists
        accommodation = get_object_or_404(Accommodation, id=accommodation_id)

        # Optional: Validate if accommodation is active/visible
        if not accommodation.is_active:
            raise ValidationError("This accommodation is currently not active")

        return Room.objects.filter(accommodation_id=accommodation_id)


@extend_schema(tags=["Host"])
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

    def validate_business_user(self, user_id):
        """Validate business user permissions"""
        user = get_object_or_404(User, id=user_id)
        if not user.is_superuser:
            raise PermissionDenied("Only business users can perform this action")
        return user

    def validate_accommodation(self, accommodation_id):
        """Validate accommodation exists and is active"""
        accommodation = get_object_or_404(Accommodation, id=accommodation_id)
        if not accommodation.is_active:
            raise ValidationError("Cannot add rooms to inactive accommodation")
        return accommodation

    def validate_room_limits(self, accommodation):
        """Validate room creation limits"""
        MAX_ROOMS_PER_ACCOMMODATION = 50
        current_rooms = Room.objects.filter(accommodation=accommodation).count()

        if current_rooms >= MAX_ROOMS_PER_ACCOMMODATION:
            raise ValidationError(f"Maximum room limit ({MAX_ROOMS_PER_ACCOMMODATION}) reached")

        # Check daily creation limit
        today_rooms = Room.objects.filter(accommodation=accommodation, created_at__date=timezone.now().date()).count()

        if today_rooms >= 10:  # 하루 최대 10개 방 생성 제한
            raise ValidationError("Daily room creation limit reached")

    @transaction.atomic
    def perform_create(self, serializer):
        accommodation_id = self.request.data.get("accommodation")
        business_user = self.validate_business_user(self.request.user.id)
        accommodation = self.validate_accommodation(accommodation_id)

        # Validate ownership
        if accommodation.host_id != business_user.id:
            raise PermissionDenied("You don't have permission to add rooms to this accommodation")

        self.validate_room_limits(accommodation)

        try:
            room = serializer.save()
            RoomInventory.objects.create(room=room, count_room=1)
        except Exception as e:
            raise ValidationError(f"Failed to create room: {str(e)}")


@extend_schema(tags=["Host"])
class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

    def validate_room_status(self, room):
        """Validate if room can be modified/deleted"""
        # Check if room has any active bookings
        has_active_bookings = room.bookings.filter(check_out_date__gte=timezone.now()).exists()

        if has_active_bookings:
            raise ValidationError("Cannot modify/delete room with active bookings")

        # Check if room is part of any active promotions
        if hasattr(room, "promotions") and room.promotions.filter(end_date__gte=timezone.now()).exists():
            raise ValidationError("Cannot modify/delete room with active promotions")

    def validate_owner(self, room):
        """Validate if user owns the room"""
        if room.accommodation.host_id != self.request.user.id:
            raise PermissionDenied("You don't have permission to modify this room")

    def get_object(self):
        room = super().get_object()
        if not room.is_available:
            raise ValidationError("This room is currently not available")
        return room

    def perform_update(self, serializer):
        room = self.get_object()
        self.validate_owner(room)
        self.validate_room_status(room)

        try:
            serializer.save()
        except Exception as e:
            raise ValidationError(f"Failed to update room: {str(e)}")

    def perform_destroy(self, instance):
        self.validate_owner(instance)
        self.validate_room_status(instance)

        try:
            inventory = instance.roominventory
            inventory.count_room -= 1
            if inventory.count_room <= 0:
                inventory.delete()
            else:
                inventory.save()
            instance.delete()
        except Exception as e:
            raise ValidationError(f"Failed to delete room: {str(e)}")


@extend_schema(tags=["Host"])
class RoomImageCreateView(generics.CreateAPIView):
    serializer_class = RoomImageSerializer
    permission_classes = [AllowAny]

    def validate_image_limit(self, room):
        MAX_IMAGES_PER_ROOM = 10
        current_images = Room_Image.objects.filter(room=room).count()

        if current_images >= MAX_IMAGES_PER_ROOM:
            raise ValidationError(f"Maximum image limit ({MAX_IMAGES_PER_ROOM}) reached")

    def validate_image_upload_frequency(self, room):
        """Validate image upload frequency"""
        last_upload = Room_Image.objects.filter(room=room).order_by("-id").first()
        if last_upload and (timezone.now() - last_upload.created_at) < timedelta(minutes=5):
            raise ValidationError("Please wait 5 minutes between image uploads")

    def perform_create(self, serializer):
        room = get_object_or_404(Room, pk=self.kwargs["pk"])

        # Validate room ownership
        if room.accommodation.host_id != self.request.user.id:
            raise PermissionDenied("You don't have permission to add images to this room")

        self.validate_image_limit(room)
        self.validate_image_upload_frequency(room)

        try:
            serializer.save(room=room)
        except Exception as e:
            raise ValidationError(f"Failed to upload image: {str(e)}")


@extend_schema(tags=["Host"])
class RoomImageDetailView(generics.DestroyAPIView):
    queryset = Room_Image.objects.all()
    serializer_class = RoomImageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Room_Image.objects.select_related("room", "room__accommodation").all()

    def validate_image_deletion(self, instance):
        """이미지 삭제 가능 여부 검증"""
        # 최소 이미지 개수 확인
        remaining_images = Room_Image.objects.filter(room=instance.room).count()
        if remaining_images <= 1:
            raise ValidationError("Cannot delete the last image of the room")

        # 대표 이미지인지 확인 (만약 대표 이미지 필드가 있다면)
        if hasattr(instance.room, "main_image") and instance.room.main_image == instance:
            raise ValidationError("Cannot delete the main image of the room")

        # 활성 예약이 있는 경우 체크
        if instance.room.bookings.filter(check_out_date__gte=timezone.now()).exists():
            raise ValidationError("Cannot delete image while room has active bookings")

    def perform_destroy(self, instance):
        self.validate_image_deletion(instance)

        try:
            # 이미지 파일 삭제
            if instance.image:
                instance.image.delete(save=False)
            instance.delete()
        except Exception as e:
            raise ValidationError(f"Failed to delete image: {str(e)}")


@extend_schema(tags=["Host"])
class RoomTypeListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomTypeSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["is_customized"]
    ordering_fields = ["type_name"]

    def get_queryset(self):
        return RoomType.objects.select_related("room", "room__accommodation").all()

    def validate_room_type_limit(self, accommodation):
        """숙소당 룸타입 개수 제한"""
        MAX_TYPES_PER_ACCOMMODATION = 10
        current_types = RoomType.objects.filter(room__accommodation=accommodation, is_customized=True).count()

        if current_types >= MAX_TYPES_PER_ACCOMMODATION:
            raise ValidationError(
                f"Maximum room type limit ({MAX_TYPES_PER_ACCOMMODATION}) reached for this accommodation"
            )

    def validate_daily_creation_limit(self, accommodation):
        """일일 생성 제한"""
        MAX_DAILY_CREATIONS = 5
        today_created = RoomType.objects.filter(
            room__accommodation=accommodation, is_customized=True, created_at__date=timezone.now().date()
        ).count()

        if today_created >= MAX_DAILY_CREATIONS:
            raise ValidationError(f"Daily room type creation limit ({MAX_DAILY_CREATIONS}) reached")

    def validate_accommodation_status(self, accommodation):
        """숙소 상태 검증"""
        if not accommodation.is_active:
            raise ValidationError("Cannot add room types to inactive accommodation")

    @transaction.atomic
    def perform_create(self, serializer):
        room = serializer.validated_data.get("room")
        is_customized = serializer.validated_data.get("is_customized", False)

        if not room or not hasattr(room, "accommodation"):
            raise ValidationError("Invalid room data")

        accommodation = room.accommodation

        # 숙소 상태 검증
        self.validate_accommodation_status(accommodation)

        # 커스텀 타입 생성 시 추가 검증
        if is_customized:
            self.validate_room_type_limit(accommodation)
            self.validate_daily_creation_limit(accommodation)

        try:
            return serializer.save()
        except IntegrityError:
            raise ValidationError("Room type creation failed - integrity error")
        except Exception as e:
            raise ValidationError(f"Room type creation failed: {str(e)}")

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Failed to create room type"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            accommodation_id = request.query_params.get("accommodation_id")
            if accommodation_id:
                # 특정 숙소의 룸타입만 조회
                self.queryset = self.get_queryset().filter(room__accommodation_id=accommodation_id)

            response = super().list(request, *args, **kwargs)

            # 메타데이터 추가
            if accommodation_id:
                accommodation = Accommodation.objects.get(id=accommodation_id)
                custom_types_count = RoomType.objects.filter(
                    room__accommodation=accommodation, is_customized=True
                ).count()

                response.data = {
                    "results": response.data,
                    "meta": {
                        "total_custom_types": custom_types_count,
                        "max_types_limit": 10,
                        "available_slots": 10 - custom_types_count,
                    },
                }

            return response
        except Exception as e:
            return Response({"error": "Failed to retrieve room types"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=["Host"])
class RoomTypeCustomCreateView(generics.CreateAPIView):
    serializer_class = RoomTypeSerializer
    permission_classes = [AllowAny]

    def validate_custom_type(self, data):
        """Validate custom type creation"""
        if RoomType.objects.filter(
            type_name=data["type_name"], is_customized=True, room__accommodation__host=self.request.user
        ).exists():
            raise ValidationError("You already have a custom type with this name")

    def perform_create(self, serializer):
        self.validate_custom_type(serializer.validated_data)
        try:
            serializer.save(is_customized=True)
        except Exception as e:
            raise ValidationError(f"Failed to create custom room type: {str(e)}")


@extend_schema(tags=["Host"])
class RoomTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        쿼리 최적화
        """
        return RoomType.objects.select_related("room", "room__accommodation").all()

    def validate_modification(self, instance):
        """기본 타입 수정/삭제 제한"""
        if not instance.is_customized:
            raise ValidationError("Cannot modify or delete basic room types")

    def validate_type_name(self, value, instance):
        """타입 이름 검증"""
        if not value or len(value.strip()) < 2:
            raise ValidationError("Room type name must be at least 2 characters long")

        # 특수문자 검사
        import re

        if not re.match("^[a-zA-Z0-9가-힣\s\-_]+$", value):
            raise ValidationError("Room type name can only contain letters, numbers, spaces, hyphens and underscores")

        # 중복 검사 (자기 자신 제외)
        if RoomType.objects.filter(type_name=value, is_customized=True).exclude(id=instance.id).exists():
            raise ValidationError("This custom type name already exists")

    def validate_room_usage(self, instance):
        """룸타입 사용중 여부 검증"""
        # 예약이 있는 방에서 사용중인지 확인
        if Room.objects.filter(roomtype=instance, bookings__check_out_date__gte=timezone.now()).exists():
            raise ValidationError("Cannot modify/delete room type that is in use by active bookings")

        # 프로모션에서 사용중인지 확인
        if (
            hasattr(instance.room, "promotions")
            and instance.room.promotions.filter(end_date__gte=timezone.now()).exists()
        ):
            raise ValidationError("Cannot modify/delete room type that is in use by active promotions")

    def perform_update(self, serializer):
        instance = self.get_object()
        self.validate_modification(instance)

        # 타입 이름 변경 시 검증
        new_name = serializer.validated_data.get("type_name")
        if new_name and new_name != instance.type_name:
            self.validate_type_name(new_name, instance)

        self.validate_room_usage(instance)

        try:
            return serializer.save()
        except Exception as e:
            raise ValidationError(f"Failed to update room type: {str(e)}")

    def perform_destroy(self, instance):
        self.validate_modification(instance)
        self.validate_room_usage(instance)

        try:
            instance.delete()
        except Exception as e:
            raise ValidationError(f"Failed to delete room type: {str(e)}")


@extend_schema(tags=["Host"])
class RoomInventoryUpdateView(generics.UpdateAPIView):
    queryset = RoomInventory.objects.all()
    serializer_class = RoomInventorySerializer
    permission_classes = [AllowAny]

    def validate_inventory_change(self, instance, new_count):
        """Validate inventory changes"""
        # Check for active bookings
        if instance.room.bookings.filter(check_out_date__gte=timezone.now()).exists():
            raise ValidationError("Cannot modify inventory with active bookings")

        # Prevent large sudden changes
        if abs(new_count - instance.count_room) > 10:
            raise ValidationError("Cannot change inventory by more than 10 rooms at once")

    def perform_update(self, serializer):
        instance = self.get_object()

        # Validate room ownership
        if instance.room.accommodation.host_id != self.request.user.id:
            raise PermissionDenied("You don't have permission to modify this inventory")

        new_count = serializer.validated_data.get("count_room")
        self.validate_inventory_change(instance, new_count)

        try:
            instance = serializer.save()
            if instance.count_room <= 0:
                instance.delete()
        except Exception as e:
            raise ValidationError(f"Failed to update inventory: {str(e)}")


@extend_schema(tags=["Host"])
class RoomInventoryListView(generics.ListAPIView):
    serializer_class = RoomInventorySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["room__accommodation", "room__is_available"]
    ordering_fields = ["count_room", "room__price"]

    def get_queryset(self):
        """
        쿼리 최적화 및 기본 필터링
        """
        queryset = RoomInventory.objects.select_related("room", "room__accommodation")

        # 재고가 있는 방만 필터링
        if self.request.query_params.get("available_only") == "true":
            queryset = queryset.filter(count_room__gt=0)

        # 가격 범위 필터링
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price:
            queryset = queryset.filter(room__price__gte=min_price)
        if max_price:
            queryset = queryset.filter(room__price__lte=max_price)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # 메타데이터 추가
        accommodation_id = request.query_params.get("room__accommodation")
        if accommodation_id:
            try:
                accommodation = Accommodation.objects.get(id=accommodation_id)
                total_inventory = sum(item.get("count_room", 0) for item in response.data)
                available_rooms = sum(1 for item in response.data if item.get("count_room", 0) > 0)

                response.data = {
                    "results": response.data,
                    "meta": {
                        "total_inventory": total_inventory,
                        "total_rooms": len(response.data),
                        "available_rooms": available_rooms,
                        "accommodation_name": accommodation.name,
                        "last_updated": timezone.now(),
                    },
                }
            except Accommodation.DoesNotExist:
                raise ValidationError("Invalid accommodation ID")

        return response
