# 20241024 수정
import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F, Prefetch
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import filters, generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.fields import ImageField, ListField
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accommodations.models import Accommodation
from apps.amenities.models import Option, RoomOption
from apps.amenities.serializers.amenities_serializers import (
    OptionSerializer,
    RoomOptionSerializer,
)
from apps.bookings.models import Booking
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType
from apps.rooms.serializers import room_serializer as serializers
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


class RoomListCreateView(BaseRoomView, APIView):
    """Room 목록 조회 및 생성"""

    parser_classes = (MultiPartParser, FormParser)
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]  # [isauthentication, ishost]

    @extend_schema(
        request=inline_serializer(
            name="RoomCreateRequest",
            fields={
                "room": serializers.RoomSerializer(),
                "images": ListField(child=ImageField(), help_text="방에 업로드할 이미지 파일들"),
                "room_type": serializers.RoomTypeSerializer(),
                "inventory": serializers.RoomInventorySerializer(),
                "options": inline_serializer(
                    name="OptionsRequest",
                    fields={"new": OptionSerializer(many=True), "default": RoomOptionSerializer(many=True)},
                ),
            },
        ),
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=serializers.RoomSerializer, description="방이 성공적으로 생성되었습니다."
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response={"type": "object", "properties": {"detail": {"type": "string"}, "code": {"type": "string"}}},
                description="잘못된 요청: 입력 값이 유효하지 않습니다.",
            ),
        },
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            data = {
                "room": json.loads(request.data.get("room")),
                "room_type": json.loads(request.data.get("room_type")),
                "inventory": json.loads(request.data.get("inventory")),
                "options": json.loads(request.data.get("options")),
                "images": request.FILES.getlist("images"),
            }

            request_data = self.validate_room_data(data)

            # 1. create room model
            room_data = request_data.get("room")
            room_serializer = serializers.RoomSerializer(data=room_data)
            if not room_serializer.is_valid():
                return Response(room_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            room = room_serializer.save()

            # 2. 이미지 처리
            image_data = [{"image": image, "room": room.id} for image in request_data["images"]]
            image_response_data = []
            for data in image_data:
                image_serializer = serializers.RoomImageSerializer(data=data)
                if not image_serializer.is_valid():
                    return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                image_serializer.save()
                image_response_data.append(image_serializer.data)

            # 3. create room type
            type_serializer = serializers.RoomTypeSerializer(
                data=request_data.get("room_type"),
            )
            if not type_serializer.is_valid():
                return Response(type_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            type_serializer.save(room=room)

            # 4. create room inventory
            inventory_serializer = serializers.RoomInventorySerializer(
                data=request_data.get("inventory"),
            )
            if not inventory_serializer.is_valid():
                return Response(inventory_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # 5. 옵션처리
            options_data = request_data["options"]  # get 대신
            new_options = options_data["new"]  # dictionary key로
            default_options = options_data["default"]
            option_response_data = []
            if new_options:
                for data in new_options:
                    new_option_serializer = OptionSerializer(data=data)
                    if not new_option_serializer.is_valid():
                        return Response(new_option_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    created_option = new_option_serializer.save()

                    # ���로 생성된 ��션을 ��소와 연결
                    RoomOption.objects.create(room=room, option=created_option, custom_value=None)
                    option_response_data.append(new_option_serializer.data)

            if default_options:
                for default_option in default_options:
                    option_id = default_option["option_id"]  # get 대신
                    if option_id:
                        try:
                            option = Option.objects.get(id=option_id)
                            RoomOption.objects.create(
                                room=room,
                                option=option,
                                custom_value=default_option.get("custom_value", None),
                            )
                            option.is_custom = False
                            option.save()

                            option_serializer = OptionSerializer(option)
                            option_response_data.append(option_serializer.data)
                        except Option.DoesNotExist:
                            return Response(
                                {"error": f"Option with id {option_id} does not exist"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
            return Response(
                {
                    "room": room_serializer.data,
                    "images": image_response_data,
                    "room_type": type_serializer.data,
                    "inventory": inventory_serializer.data,
                    "options": option_response_data,
                },
                status=status.HTTP_201_CREATED,
            )
        except json.JSONDecodeError as e:
            return Response({"error": "잘못된 JSON 형식입니다.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    def validate_room_data(self, request_data):
        if not request_data.get("room"):
            raise ValidationError({"room": "방 정보가 누락되었습니다."})
        if not request_data.get("images"):
            raise ValidationError({"images": "방 이미지가 누락되었습니다."})
        if not request_data.get("room_type"):
            raise ValidationError({"room_type": "방 유형 정보가 누락되었습니다."})
        if not request_data.get("inventory"):
            raise ValidationError({"inventory": "인벤토리 정보가 누락되었습니다."})
        if not request_data.get("options"):
            raise ValidationError({"options": "옵션 정보가 누락되었습니다."})

        return request_data

    def process_room_type(self, type_data):
        if isinstance(type_data, dict):
            type_data["is_customized"] = True
            type_serializer = RoomTypeSerializer(data=type_data)
            if type_serializer.is_valid():
                return type_serializer.save()
            raise ValidationError(type_serializer.errors)
        else:
            return get_object_or_404(RoomType, id=type_data)


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
