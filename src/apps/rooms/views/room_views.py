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
from apps.common.choices import OPTION_CHOICES
from apps.common.permissions.host_permission import IsHost
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType
from apps.rooms.serializers import room_serializer as serializers
from apps.rooms.serializers.room_serializer import (
    BedOptionSerializer,
    RoomImageSerializer,
    RoomInventorySerializer,
    RoomQuantitySerializer,
    RoomSerializer,
    RoomTypeSerializer,
    RoomUpdateSerializer,
)

User = get_user_model()


class BaseRoomView:
    """기본 Room 뷰"""

    permission_classes = [AllowAny]  # [IsAuthenticated, IsHost]


class RoomListCreateView(BaseRoomView, APIView):
    """Room 목록 조회 및 생성"""

    parser_classes = (MultiPartParser, FormParser)
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated, IsHost]

    @extend_schema(
        request=inline_serializer(
            name="RoomCreateRequest",
            fields={
                "room": serializers.RoomSerializer(),
                "images": ListField(
                    child=ImageField(), help_text="독채가 아닐 경우 방에 업로드할 이미지 파일들", required=False
                ),
                "room_type": serializers.RoomTypeSerializer(help_text="독채가 아닐 경우 방의 유형", required=False),
                "inventory": serializers.RoomInventorySerializer(help_text="독채일 경우 count_room은 1밖에 안됨"),
                "options": inline_serializer(
                    name="OptionsRequest",
                    fields={"new": OptionSerializer(many=True), "default": RoomOptionSerializer(many=True)},
                ),
                "bed_options": serializers.BedOptionSerializer(many=True),
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
                "room_type": json.loads(request.data.get("room_type", "{}")),
                "inventory": json.loads(request.data.get("inventory")),
                "options": json.loads(request.data.get("options")),
                "bed_options": (
                    [json.loads(request.data.get("bed_options"))]
                    if isinstance(json.loads(request.data.get("bed_options", "{}")), dict)
                    else json.loads(request.data.get("bed_options", "[]"))
                ),
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
                context={"request": request},
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
            inventory_serializer.save(room=room)

            # 5. 침대옵션 처리
            bed_options_data = request_data["bed_options"]
            bed_option_response_data = []

            for bed_option in bed_options_data:
                bed_serializer = BedOptionSerializer(data=bed_option)
                if not bed_serializer.is_valid():
                    return Response(bed_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                option = Option.objects.create(name=bed_option["bed_type"], category="bed", is_custom=False)

                RoomOption.objects.create(room=room, option=option, custom_value=None)  # 그냥 None으로 설정

                response_serializer = BedOptionSerializer(option, context={"quantity": bed_option["quantity"]})
                bed_option_response_data.append(response_serializer.data)

            # 6. room_quantity 처리
            room_quantity_data = request_data.get("room_quantity")
            room_quantity_response_data = None

            if room_quantity_data:
                quantity_serializer = RoomQuantitySerializer(data=room_quantity_data)
                if not quantity_serializer.is_valid():
                    return Response(quantity_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                option = Option.objects.create(name="room_quantity", category="room_structure", is_custom=False)

                RoomOption.objects.create(
                    room=room, option=option, custom_value=str(room_quantity_data["room_quantity"])
                )

                room_quantity_response_data = quantity_serializer.data

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
                    "bed_options": bed_option_response_data,
                    # "room_quantity": room_quantity_response_data,
                },
                status=status.HTTP_201_CREATED,
            )
        except json.JSONDecodeError as e:
            return Response({"error": "잘못된 JSON 형식입니다.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    def validate_room_data(self, request_data):
        # 1. 숙소 타입 확인 (accommodation 데이터 가져오기)
        room_data = request_data.get("room")
        if not room_data:
            raise ValidationError({"room": "방 정보가 누락되었습니다."})

        # accommodation_id로 숙소 정보 조회
        accommodation = get_object_or_404(Accommodation, id=room_data.get("accommodation"))
        is_whole_house = "독채" in accommodation.accommodationtype.type_name

        # 2. 일반 숙소인 경우 모든 필수 데이터 검증
        if not is_whole_house:
            if not request_data.get("images"):
                raise ValidationError({"images": "방 이미지가 누락되었습니다."})
            if not request_data.get("room_type", {}).get("type_name"):
                raise ValidationError({"room_type": "방 유형 정보가 누락되었습니다."})
            if not room_data.get("name"):
                raise ValidationError({"name": "방 이름이 누락되었습니다."})
            if not room_data.get("description"):
                raise ValidationError({"description": "방 설명이 누락되었습니다."})

        if not request_data.get("inventory"):
            raise ValidationError({"inventory": "인벤토리 정보가 누락되었습니다."})
        if not request_data.get("options"):
            raise ValidationError({"options": "옵션 정보가 누락되었습니다."})

        # 3. 독채인 경우 기본값 설정
        if is_whole_house:
            if request_data.get("room_type"):
                del request_data["room_type"]
                raise ValidationError({"room_type": "독채는 객실의 유형이 필요없습니다."})
            if request_data.get("images"):
                del request_data["images"]
                raise ValidationError({"images": "독채는 숙소에서 이미지를 등록해주세요."})
            room_data["name"] = accommodation.name
            room_data["description"] = accommodation.description
            inventory_data = request_data.get("inventory", {})
            if inventory_data.get("count_room") != 1:
                raise ValidationError({"count_room": "독채는 한 개의 숙소만 등록 가능합니다."})

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
        kwargs["partial"] = True  # PATCH 메서드를 위해 partial=True로 설정
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
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
        kwargs["partial"] = True  # partial update 허용
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
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
        kwargs["partial"] = True  # PATCH 메서드를 위해 partial=True로 설정
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class OptionChoicesView(APIView):
    permission_classes = [AllowAny]  # [IsAuthenticated, IsHost]

    @extend_schema(
        summary="옵션 선택지 목록 조회",
        description="사용 가능한 옵션 선택지 목록을 반환합니다.",
        responses={
            200: {
                "type": "array",
                "items": {"type": "object", "properties": {"value": {"type": "string"}, "label": {"type": "string"}}},
            }
        },
    )
    def get(self, request):
        choices = [choice[0] for choice in OPTION_CHOICES]  # value만 반환
        return Response(choices)
