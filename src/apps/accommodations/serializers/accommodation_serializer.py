from rest_framework import serializers

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    AccommodationType,
    GPS_Info,
)


class AccommodationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationType
        fields = ["is_customized", "type_name"]


class AccommodationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation_Image
        fields = ["id", "image"]


class GPSInfoSerializer(serializers.ModelSerializer):
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = GPS_Info
        fields = [
            "city",
            "states",
            "road_name",
            "address",
            "latitude",
            "longitude",
            "coordinates",
        ]

    def get_coordinates(self, obj):
        return {"lat": obj.latitude, "lon": obj.longitude}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["coordinates"] = self.get_coordinates(instance)
        return ret


class AccommodationSerializer(serializers.ModelSerializer):
    accommodation_type = AccommodationTypeSerializer(source="accommodationtype", read_only=True)
    images = AccommodationImageSerializer(many=True, read_only=True)
    gps_info = GPSInfoSerializer(read_only=True)

    class Meta:
        model = Accommodation
        fields = [
            "id",
            "host",
            "name",
            "phone_number",
            "description",
            "rules",
            "average_rating",
            "is_active",
            "created_at",
            "updated_at",
            "accommodation_type",
            "images",
            "gps_info",
        ]
        read_only_fields = ["id", "host", "average_rating", "created_at", "updated_at"]

    def create(self, validated_data):
        return Accommodation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
