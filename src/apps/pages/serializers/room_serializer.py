from typing import Any, Dict, List

from rest_framework import serializers

from apps.accommodations.models import Accommodation
from apps.amenities.models import Option, RoomOption
from apps.pages.services.money_view_service import MoneyViewService
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType


# 룸 이미지 시리얼라이저
class RoomImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Image
        fields = ["image"]


# 옵션 시리얼라이저
class RoomOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["name", "category", "is_custom"]


# 룸 단위 옵션 시리얼라이저
class RoomRoomOptionSerializer(serializers.ModelSerializer):
    option = RoomOptionSerializer()

    class Meta:
        model = RoomOption
        fields = ["option"]


# 룸 인벤토리 시리얼라이저
class RoomInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInventory
        fields = ["count_room"]


# 룸 타입 시리얼라이저
class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = "__all__"


# 침대 정보 시리얼라이저
class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "category", "name"]


class RoomSerializer(serializers.ModelSerializer):
    bed_info = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    room_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "capacity",
            "max_capacity",
            "description",
            "price",
            "check_in_time",
            "check_out_time",
            "bed_info",
            "room_count",
        ]

    def get_price(self, obj: Room) -> str:
        price = obj.price
        money_view = MoneyViewService()
        money_price = money_view.format(price)
        return money_price

    def get_bed_info(self, obj: Room) -> Dict[str, Any]:
        bed_options = RoomOption.objects.filter(room=obj.id, option__category="bed")
        bed_total_count = sum(option.custom_value for option in bed_options)
        bed_type_num = [{option.option.name: option.custom_value} for option in bed_options]

        return {"total_beds": bed_total_count, "bed_type_num": bed_type_num}

    def get_room_count(self, obj: Room) -> int:
        room_structure = RoomOption.objects.filter(room=obj.id, option__category="structure").first()
        if room_structure:
            return room_structure.custom_value
        return 0


class RoomDetailSerializer(RoomSerializer):
    room = serializers.SerializerMethodField()
    accommodation_name = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    room_options = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["accommodation_name", "room", "room_options", "images"]

    def get_accommodation_name(self, obj: Room) -> str:
        return Accommodation.objects.get(pk=obj.accommodation_id).name

    def get_room(self, obj: Room) -> Dict[str, Any]:
        return RoomSerializer(Room.objects.get(pk=obj.id)).data

    def get_images(self, obj: Room):
        images = Room_Image.objects.filter(room=obj.id)
        return RoomImagesSerializer(images, many=True).data

    def get_room_options(self, obj: Room) -> List[Dict[str, Any]]:
        options = RoomOption.objects.filter(room=obj.id)
        options_data = []

        for room_option in options:
            option_data = {
                "id": room_option.option.id,
                "name": room_option.option.name,
                "category": room_option.option.category,
                "is_custom": room_option.option.is_custom,
                "custom_value": room_option.custom_value,  # Assuming custom_value is an attribute of RoomOption
            }
            options_data.append(option_data)

        return options_data


class RoomResponseSerializer(serializers.ModelSerializer):
    representative_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "capacity",
            "max_capacity",
            "price",
            "is_available",
            "representative_image",
            "check_in_time",
            "check_out_time",
        ]

    def get_representative_image(self, obj):
        image = Room_Image.objects.filter(room=obj, is_representative=True).first()
        return image.image.url if image else None

    def get_price(self, obj):
        return f"{obj.price:,}"
