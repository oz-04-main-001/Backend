from rest_framework import serializers

from apps.accommodations.models import Accommodation
from apps.amenities.models import RoomOption
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType


# 룸 사진들
class RoomImagesSerializer(serializers.Serializer):
    class Meta:
        model = Room_Image
        fields = [
            "image",
        ]


# 룸 옵션
class RoomOptionSerializer(serializers.Serializer):
    class Meta:
        model = RoomOption
        fields = "__all__"


# 룸 갯수
class RoomInventorySerializer(serializers.Serializer):
    class Meta:
        model = RoomInventory
        fields = "__all__"


# 룸 타입
class RoomTypeSerializer(serializers.Serializer):
    class Meta:
        model = RoomType
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    accommodation_name = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            "id",
            "accommodation_name",
            "name",
            "capacity",
            "max_capacity",
            "description",
            "price",
            "check_in_time",
            "check_out_time",
            "images",
        ]

    def get_accommodation_name(self, obj):
        accommodation = Accommodation.objects.get(pk=obj.accommodation_id)
        return accommodation.name

    def get_images(self, obj):
        images = Room_Image.objects.filter(room=obj.id)
        serializer = RoomImagesSerializer(images, many=True)
        return serializer.data
