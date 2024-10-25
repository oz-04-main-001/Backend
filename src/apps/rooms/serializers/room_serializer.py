# room_serializer.py
from django.utils import timezone
from rest_framework import serializers

from apps.amenities.models import Option
from apps.amenities.serializers.amenities_serializers import OptionSerializer
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ["is_customized", "type_name", "room"]
        extra_kwargs = {"is_customized": {"required": False}, "room": {"required": True, "write_only": True}}

    def validate_type_name(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Room type name must be at least 2 characters long")

        import re

        if not re.match("^[a-zA-Z0-9가-힣\s\-_]+$", value):
            raise serializers.ValidationError(
                "Room type name can only contain letters, numbers, spaces, hyphens and underscores"
            )

        is_customized = self.initial_data.get("is_customized", False)
        if is_customized and RoomType.objects.filter(type_name=value, is_customized=True).exists():
            raise serializers.ValidationError("This custom type name already exists")

        return value.strip()


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Image
        fields = ["id", "image"]

    def validate_image(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size cannot exceed 5MB")

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
    room_type = RoomTypeSerializer(source="roomtype")
    images = RoomImageSerializer(many=True, read_only=True)
    upload_images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=True)
    inventory = RoomInventorySerializer(source="roominventory")
    options = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Option.objects.all(), required=False, write_only=True
    )
    custom_options = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)

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
            "upload_images",
            "inventory",
            "options",
            "custom_options",
        ]

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
        if check_in and check_out and check_in >= check_out:
            raise serializers.ValidationError({"check_in_time": "Check-in time must be before check-out time"})

        if len(data["name"]) < 2:
            raise serializers.ValidationError({"name": "Room name must be at least 2 characters long"})

        # 이미지 validation
        if not data.get("upload_images"):
            raise serializers.ValidationError({"upload_images": "At least one image is required"})

        return data

    def create(self, validated_data):
        room_type_data = validated_data.pop("roomtype")
        upload_images = validated_data.pop("upload_images")
        inventory_data = validated_data.pop("roominventory")
        options_data = validated_data.pop("options", [])
        custom_options_data = validated_data.pop("custom_options", [])

        # 1. Room 생성
        room = Room.objects.create(**validated_data)

        # 2. RoomType 생성
        room_type_data["room"] = room
        RoomType.objects.create(**room_type_data)

        # 3. RoomInventory 생성
        RoomInventory.objects.create(room=room, **inventory_data)

        # 4. Room Images 생성
        image_instances = []
        for image in upload_images:
            image_instances.append(Room_Image(room=room, image=image))
        if image_instances:
            Room_Image.objects.bulk_create(image_instances)

        # 5. Room Options 생성
        from apps.amenities.models import RoomOption

        # 기존 옵션 처리
        option_instances = [RoomOption(room=room, option=option) for option in options_data]

        # 커스텀 옵션 처리
        for option_data in custom_options_data:
            option = Option.objects.create(
                name=option_data["name"], category=option_data.get("category", "extra"), is_custom=True
            )
            option_instances.append(
                RoomOption(room=room, option=option, custom_value=option_data.get("custom_value", ""))
            )

        if option_instances:
            RoomOption.objects.bulk_create(option_instances)

        return room


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
