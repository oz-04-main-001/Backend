from rest_framework import serializers

from ..models import AccommodationAmenity, Amenity, Option, RoomOption


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["id", "name", "category", "description", "icon", "is_custom"]


class AccommodationAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer(read_only=True)
    amenity_id = serializers.PrimaryKeyRelatedField(queryset=Amenity.objects.all(), write_only=True)

    class Meta:
        model = AccommodationAmenity
        fields = ["id", "accommodation", "amenity", "amenity_id", "custom_value"]

    def create(self, validated_data):
        amenity = validated_data.pop("amenity_id")
        return AccommodationAmenity.objects.create(amenity=amenity, **validated_data)


class DetailedAccommodationAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer(read_only=True)

    class Meta:
        model = AccommodationAmenity
        fields = ["id", "amenity", "custom_value"]


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "name", "category", "is_custom"]


class DetailedRoomOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(read_only=True)

    class Meta:
        model = RoomOption
        fields = ["id", "option", "custom_value"]


class RoomOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(read_only=True)
    option_id = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(), write_only=True)

    class Meta:
        model = RoomOption
        fields = ["id", "room", "option", "option_id", "custom_value"]

    def create(self, validated_data):
        option = validated_data.pop("option_id")
        return RoomOption.objects.create(option=option, **validated_data)
