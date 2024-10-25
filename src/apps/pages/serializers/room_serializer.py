from rest_framework import serializers

from apps.accommodations.models import Accommodation
from apps.amenities.models import Option, RoomOption
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
        fields = "__all__"


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
        ]

    def get_bed_info(self, obj):
        bed_options = RoomOption.objects.filter(room=obj.id, option__category="bed")
        bed_count = sum(option.custom_value for option in bed_options)
        bed_names = list(set(option.option.name for option in bed_options))
        return {"total_beds": bed_count, "bed_names": bed_names}


class RoomDetailSerializer(RoomSerializer):
    room = serializers.SerializerMethodField()
    accommodation_name = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    room_options = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["accommodation_name", "room", "room_options", "images"]

    def get_accommodation_name(self, obj):
        return Accommodation.objects.get(pk=obj.accommodation_id).name

    def get_room(self, obj):
        return RoomSerializer(Room.objects.get(pk=obj.id)).data

    def get_images(self, obj):
        images = Room_Image.objects.filter(room=obj.id)
        return RoomImagesSerializer(images, many=True).data

    def get_room_options(self, obj):
        options = RoomOption.objects.filter(room=obj.id)
        return RoomRoomOptionSerializer(options, many=True).data
