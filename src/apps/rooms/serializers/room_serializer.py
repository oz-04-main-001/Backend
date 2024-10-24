# 20241024 수정
from django.utils import timezone
from rest_framework import serializers

from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ["is_customized", "type_name", "room"]
        extra_kwargs = {"is_customized": {"required": False}, "room": {"required": True, "write_only": True}}

    def validate_type_name(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Room type name must be at least 2 characters long")

        # 특수문자 검사 (일부 기본 특수문자 허용)
        import re

        if not re.match("^[a-zA-Z0-9가-힣\s\-_]+$", value):
            raise serializers.ValidationError(
                "Room type name can only contain letters, numbers, spaces, hyphens and underscores"
            )

        # 중복 이름 검사 - 커스텀 타입의 경우
        is_customized = self.initial_data.get("is_customized", False)
        if is_customized and RoomType.objects.filter(type_name=value, is_customized=True).exists():
            raise serializers.ValidationError("This custom type name already exists")

        return value.strip()

    def validate_room(self, value):
        if not isinstance(value, Room):
            raise serializers.ValidationError("Invalid room format")

        # 이미 룸타입이 있는지 확인
        if RoomType.objects.filter(room=value).exists():
            raise serializers.ValidationError("This room already has a room type assigned")

        return value

    def validate(self, data):
        # 기본값 설정
        if "is_customized" not in data:
            data["is_customized"] = False

        if not data.get("room"):
            raise serializers.ValidationError({"room": "Room field is required"})

        # 기본 타입인 경우 system reserved name 검사
        if not data.get("is_customized"):
            reserved_names = ["standard", "deluxe", "suite"]
            if data.get("type_name").lower() not in reserved_names:
                raise serializers.ValidationError(
                    {"type_name": "Basic room type must be one of: standard, deluxe, suite"}
                )

        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create room type: {str(e)}")

    def update(self, instance, validated_data):
        # 기본 타입은 수정 불가
        if not instance.is_customized:
            raise serializers.ValidationError("Cannot modify basic room types")

        try:
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update room type: {str(e)}")


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Image
        fields = ["id", "image"]

    def validate_image(self, value):
        # Check file size (limit to 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size cannot exceed 5MB")

        # Check file extension
        valid_extensions = [".jpg", ".jpeg", ".png", ".gif"]
        import os

        ext = os.path.splitext(value.name)[1]
        if not ext.lower() in valid_extensions:
            raise serializers.ValidationError("Unsupported file extension. Use jpg, jpeg, png or gif")

        return value


class RoomInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInventory
        fields = ["count_room"]

    def validate_count_room(self, value):
        if value < 0:
            raise serializers.ValidationError("Room count cannot be negative")
        return value


class RoomSerializer(serializers.ModelSerializer):
    room_type = RoomTypeSerializer(source="roomtype", read_only=True)
    images = RoomImageSerializer(many=True, read_only=True)
    inventory = RoomInventorySerializer(source="roominventory", read_only=True)

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
            "room_type",
            "images",
            "inventory",
        ]

    def validate(self, data):
        # 필수 필드 검증
        if not data.get("capacity"):
            raise serializers.ValidationError({"capacity": "Capacity is required"})

        if not data.get("max_capacity"):
            raise serializers.ValidationError({"max_capacity": "Maximum capacity is required"})

        if not data.get("price"):
            raise serializers.ValidationError({"price": "Price is required"})

        if not data.get("name"):
            raise serializers.ValidationError({"name": "Name is required"})

        # 1. capacity validation
        if data["capacity"] > data["max_capacity"]:
            raise serializers.ValidationError({"capacity": "Capacity cannot be greater than max capacity"})

        if data["capacity"] <= 0:
            raise serializers.ValidationError({"capacity": "Capacity must be greater than 0"})

        # 2. price validation
        if data["price"] <= 0:
            raise serializers.ValidationError({"price": "Price must be greater than 0"})

        # 3. check-in/out time validation
        check_in = data.get("check_in_time")
        check_out = data.get("check_out_time")

        if check_in and check_out:  # 선택적 필드이므로 둘 다 있을 때만 검증
            if check_in >= check_out:
                raise serializers.ValidationError({"check_in_time": "Check-in time must be before check-out time"})

        # 4. name validation
        if len(data["name"]) < 2:
            raise serializers.ValidationError({"name": "Room name must be at least 2 characters long"})

        return data
