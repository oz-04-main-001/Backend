# room_serializer.py
from django.utils import timezone
from rest_framework import serializers

from apps.amenities.models import Option
from apps.amenities.serializers.amenities_serializers import OptionSerializer
from apps.common.choices import ROOM_TYPE_CHOICES
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ["is_customized", "type_name"]  # room 필드 제거
        extra_kwargs = {
            "is_customized": {"default": False},  # 커스텀 타입 허용
        }

    def validate(self, data):
        type_name = data.get("type_name", "").lower()
        data["type_name"] = type_name
        is_customized = data.get("is_customized", False)
        valid_types = [choice[0] for choice in ROOM_TYPE_CHOICES]

        if not is_customized and type_name not in valid_types:
            raise serializers.ValidationError(
                f"'{type_name}'은(는) 유효한 방 유형이 아닙니다. "
                f"다음 중 하나를 선택하세요: {', '.join(valid_types)}"
                f" 또는 커스텀 타입으로 설정하려면 is_customized를 true로 설정하세요."
            )

        return data


class RoomImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(
        use_url=True,
        required=True,
        allow_empty_file=True,
        error_messages={
            "invalid": "유효한 이미지 파일이 아닙니다.",
            "empty": "이미지 파일이 비어있습니다.",
            "invalid_image": "올바른 이미지 파일 형식이 아닙니다.",
        },
    )

    class Meta:
        model = Room_Image
        fields = ["id", "room", "image", "image_url"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def validate_image(self, value):
        if value:
            if value.size > 10 * 1024 * 1024:  # 10MB
                raise serializers.ValidationError("이미지 크기가 10MB를 초과할 수 없습니다.")
        elif not value.get("upload_images"):
            raise serializers.ValidationError({"upload_images": "At least one image is required"})

        return value


class RoomInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInventory
        fields = ["count_room"]
        extra_kwargs = {"count_room": {"default": 1, "min_value": 1, "help_text": "방의 총 개수"}}  # 최소값 1 설정

    def validate_count_room(self, value):
        if value < 1:  # 0도 허용하지 않음
            raise serializers.ValidationError("방 개수는 최소 1개 이상이어야 합니다.")
        if value > 100:  # 적절한 최대값 설정
            raise serializers.ValidationError("방 개수가 너무 많습니다. (최대 100개)")
        return value


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "id",
            "accommodation",
            "name",
            "capacity",
            "max_capacity",
            "price",
            "stay_type",
            "description",
            "check_in_time",
            "check_out_time",
            "is_available",
        ]
        read_only_fields = ["id", "stay_type"]
        extra_kwargs = {
            "capacity": {"default": 2},
            "accommodation": {"default": 1},
            "max_capacity": {"default": 4},
            "price": {"default": 50000},
            "check_in_time": {"default": "15:00:00"},
            "check_out_time": {"default": "11:00:00"},
            "is_available": {"default": True},
        }

    def validate(self, data):
        # 기존 validation
        if not data.get("capacity"):
            raise serializers.ValidationError({"capacity": "Capacity is required"})

        if not data.get("max_capacity"):
            raise serializers.ValidationError({"max_capacity": "Maximum capacity is required"})

        if not data.get("price"):
            raise serializers.ValidationError({"price": "Price is required"})

        if not data.get("name"):
            raise serializers.ValidationError({"name": "Name is required"})

        if data["capacity"] > data["max_capacity"]:
            raise serializers.ValidationError({"capacity": "Capacity cannot be greater than max capacity"})

        if data["capacity"] <= 0:
            raise serializers.ValidationError({"capacity": "Capacity must be greater than 0"})

        if data["price"] <= 0:
            raise serializers.ValidationError({"price": "Price must be greater than 0"})

        check_in = data.get("check_in_time")
        check_out = data.get("check_out_time")
        stay_type = data.get("stay_type")
        if check_in and check_out:
            if stay_type == False:  # 대실일 경우
                if check_in >= check_out:  # 대실은 체크아웃이 체크인보다 빨라야 함
                    raise serializers.ValidationError(
                        {"check_in_time": "대실의 경우 체크아웃 시간이 체크인 시간보다 빨라야 합니다."}
                    )

            else:  # 숙박일 경우
                if check_in <= check_out:  # 숙박은 체크인이 체크아웃보다 빨라야 함
                    raise serializers.ValidationError(
                        {"check_in_time": "숙박의 경우 체크인 시간이 체크아웃 시간보다 빨라야 합니다."}
                    )
        if len(data["name"]) < 2:
            raise serializers.ValidationError({"name": "Room name must be at least 2 characters long"})

        # 이미지 validation

        return data

    def create(self, validated_data):
        validated_data["stay_type"] = True
        instance = super().create(validated_data)
        # getattr를 사용하여 더 안전하게 처리
        instance.accommodation_name = getattr(instance.accommodation, "name", None)
        instance.save()
        return instance  # 1. Room 생성

    def update(self, instance, validated_data):
        validated_data.pop("accommodation", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.accommodation_name = getattr(instance.accommodation, "name", None)
        instance.save()
        return instance


# room_serializer.py에 추가
class RoomUpdateSerializer(serializers.ModelSerializer):
    """Room 기본 정보 수정용 시리얼라이저"""

    class Meta:
        model = Room
        fields = [
            "name",
            "capacity",
            "max_capacity",
            "price",
            "stay_type",
            "description",
            "check_in_time",
            "check_out_time",
            "is_available",
        ]

    def validate(self, data):
        # capacity validation
        if "capacity" in data and "max_capacity" in data:
            if data["capacity"] > data["max_capacity"]:
                raise serializers.ValidationError({"capacity": "Capacity cannot be greater than max capacity"})
            if data["capacity"] <= 0:
                raise serializers.ValidationError({"capacity": "Capacity must be greater than 0"})

        # price validation
        if "price" in data and data["price"] <= 0:
            raise serializers.ValidationError({"price": "Price must be greater than 0"})

        # check-in/out time validation
        check_in = data.get("check_in_time")
        check_out = data.get("check_out_time")
        if check_in and check_out and check_in >= check_out:
            raise serializers.ValidationError({"check_in_time": "Check-in time must be before check-out time"})

        # name validation
        if "name" in data and len(data["name"]) < 2:
            raise serializers.ValidationError({"name": "Room name must be at least 2 characters long"})

        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
