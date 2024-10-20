from rest_framework import serializers

from ..models import Room, Room_Image, RoomInventory, RoomType


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ["is_customized", "type_name"]


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Image
        fields = ["id", "image"]


class RoomInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInventory
        fields = ["count_room"]


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

    def create(self, validated_data):
        room = Room.objects.create(**validated_data)
        RoomInventory.objects.create(room=room, count_room=1)
        return room

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
