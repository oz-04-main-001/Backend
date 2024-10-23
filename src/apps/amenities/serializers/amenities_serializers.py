# 20241023 수정
from django.core.validators import MinLengthValidator
from rest_framework import serializers

from apps.amenities.models import AccommodationAmenity, Amenity, Option, RoomOption


class AmenitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[MinLengthValidator(2, "Name must be at least 2 characters long")])

    class Meta:
        model = Amenity
        fields = ["id", "name", "category", "description", "icon", "is_custom"]

    def validate_category(self, value):
        valid_categories = ["basic", "safety", "facility", "service"]
        if value.lower() not in valid_categories:
            raise serializers.ValidationError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        return value.lower()

    def validate_icon(self, value):
        if value and len(value) < 3:
            raise serializers.ValidationError("Icon name must be at least 3 characters long")
        return value


class AccommodationAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer(read_only=True)
    amenity_id = serializers.PrimaryKeyRelatedField(queryset=Amenity.objects.all(), write_only=True)

    class Meta:
        model = AccommodationAmenity
        fields = ["id", "accommodation", "amenity", "amenity_id", "custom_value"]

    def validate(self, data):
        # 커스텀 어메니티의 경우 custom_value가 필수
        if data.get("amenity_id").is_custom and not data.get("custom_value"):
            raise serializers.ValidationError({"custom_value": "Custom value is required for custom amenities"})

        # 일반 어메니티의 경우 custom_value가 있으면 안됨
        if not data.get("amenity_id").is_custom and data.get("custom_value"):
            raise serializers.ValidationError(
                {"custom_value": "Custom value should not be set for non-custom amenities"}
            )

        return data

    def create(self, validated_data):
        amenity = validated_data.pop("amenity_id")
        try:
            return AccommodationAmenity.objects.create(amenity=amenity, **validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create accommodation amenity: {str(e)}")


class DetailedAccommodationAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer(read_only=True)

    class Meta:
        model = AccommodationAmenity
        fields = ["id", "amenity", "custom_value"]


class OptionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[MinLengthValidator(2, "Name must be at least 2 characters long")])

    class Meta:
        model = Option
        fields = ["id", "name", "category", "is_custom"]

    def validate_category(self, value):
        valid_categories = ["bed", "bathroom", "view", "extra"]
        if value.lower() not in valid_categories:
            raise serializers.ValidationError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        return value.lower()


class RoomOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(read_only=True)
    option_id = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(), write_only=True)

    class Meta:
        model = RoomOption
        fields = ["id", "room", "option", "option_id", "custom_value"]

    def validate(self, data):
        # 커스텀 옵션의 경우 custom_value가 필수
        if data.get("option_id").is_custom and not data.get("custom_value"):
            raise serializers.ValidationError({"custom_value": "Custom value is required for custom options"})

        # 일반 옵션의 경우 custom_value가 있으면 안됨
        if not data.get("option_id").is_custom and data.get("custom_value"):
            raise serializers.ValidationError({"custom_value": "Custom value should not be set for non-custom options"})

        return data

    def create(self, validated_data):
        option = validated_data.pop("option_id")
        try:
            return RoomOption.objects.create(option=option, **validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create room option: {str(e)}")


class DetailedRoomOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(read_only=True)

    class Meta:
        model = RoomOption
        fields = ["id", "option", "custom_value"]
