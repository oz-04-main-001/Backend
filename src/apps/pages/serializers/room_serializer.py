from tabnanny import check

from rest_framework import serializers

from apps.accommodations.models import Accommodation
from apps.amenities.models import RoomOption
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType


# 룸 사진
class RoomImgSerializer(serializers.Serializer):
    class Meta:
        model = Room_Image
        fields = '__all__'

# 룸 옵션
class RoomOptionSerializer(serializers.Serializer):
    class Meta:
        model = RoomOption
        fields = '__all__'

# 룸 갯수
class RoomInventorySerializer(serializers.Serializer):
    class Meta:
        model = RoomInventory
        fields = '__all__'


# 룸 타입
class RoomTypeSerializer(serializers.Serializer):
    class Meta:
        model = RoomType
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    accommodation_name = serializers.SerializerMethodField()
    class Meta:
        model = Room
        fields = ['accommodation_name','name','capacity','max_capacity', 'description','price','stay_type','check_in_time','check_out_time']

    def get_accommodation_name(self,obj):
        accommodation = Accommodation.objects.get(pk=obj.accommodation_id)
        return accommodation.name
