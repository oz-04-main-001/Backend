from django.contrib.gis.geos import Point
from rest_framework import serializers

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    AccommodationType,
    GPS_Info,
)
from apps.amenities.models import AccommodationAmenity, Amenity
from apps.amenities.serializers.amenities_serializers import (
    AccommodationAmenityUpdateSerializer,
)


# 기본 조회/생성용 시리얼라이저들
class GPSInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPS_Info
        fields = ["city", "states", "road_name", "address", "location"]

    def validate(self, data):
        """GPS 정보 유효성 검사"""
        location = data.get("location")
        if location:
            coordinates = location.get("coordinates")
            if coordinates:
                try:
                    longitude, latitude = float(coordinates[0]), float(coordinates[1])
                    if not (-90 <= latitude <= 90):
                        raise serializers.ValidationError("위도는 -90에서 90 사이의 값이어야 합니다.")
                    if not (-180 <= longitude <= 180):
                        raise serializers.ValidationError("경도는 -180에서 180 사이의 값이어야 합니다.")
                    data["location"] = Point(longitude, latitude)
                except (TypeError, ValueError, IndexError):
                    raise serializers.ValidationError("유효한 위도와 경도 값을 입력해야 합니다.")
            else:
                raise serializers.ValidationError("좌표 정보가 필요합니다.")

        if len(data.get("city", "").strip()) < 1:
            raise serializers.ValidationError("도시명은 필수입니다.")
        if len(data.get("states", "").strip()) < 1:
            raise serializers.ValidationError("시/도는 필수입니다.")
        if len(data.get("address", "").strip()) < 5:
            raise serializers.ValidationError("주소는 최소 5자 이상이어야 합니다.")
        if len(data.get("road_name", "").strip()) < 1:
            raise serializers.ValidationError("도로명은 필수입니다.")

        return data


class AccommodationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationType
        fields = ["type_name", "is_customized"]

    def validate_type_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("숙박시설 유형은 최소 2자 이상이어야 합니다.")
        return value.strip()


class AccommodationImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation_Image
        fields = ["id", "image", "image_url"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class AccommodationSerializer(serializers.ModelSerializer):
    accommodation_type = AccommodationTypeSerializer(source="accommodationtype")
    images = AccommodationImageSerializer(many=True, read_only=True)
    upload_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
    )
    gps_info = GPSInfoSerializer()
    amenities = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Amenity.objects.all(), required=False, write_only=True
    )
    custom_amenities = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    accommodation_amenities = AccommodationAmenityUpdateSerializer(
        source="accommodationamenity_set", many=True, read_only=True
    )

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
            "upload_images",  # 이미지 업로드용 필드
            "gps_info",
            "amenities",  # 기존 부대시설 선택용
            "custom_amenities",  # 커스텀 부대시설 생성용
            "accommodation_amenities",  # 조회용
        ]
        read_only_fields = ["id", "host", "average_rating", "created_at", "updated_at"]

    def validate_phone_number(self, value):
        import re

        if not re.match(r"^\d{2,3}-\d{3,4}-\d{4}$", value):
            raise serializers.ValidationError("올바른 전화번호 형식이 아닙니다. (예: 02-123-4567 또는 010-1234-5678)")
        return value.strip()

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("숙박시설 이름은 최소 2자 이상이어야 합니다.")
        return value.strip()

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("설명은 최소 10자 이상이어야 합니다.")
        return value.strip()

    def validate_rules(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("규칙은 최소 5자 이상이어야 합니다.")
        return value.strip()

    def validate_upload_images(self, value):
        if value:
            total_size = sum(image.size for image in value)
            if total_size > 50 * 1024 * 1024:  # 50MB
                raise serializers.ValidationError("전체 이미지 크기가 50MB를 초과할 수 없습니다.")

            for image in value:
                if image.size > 10 * 1024 * 1024:  # 10MB
                    raise serializers.ValidationError(f"{image.name}의 크기가 10MB를 초과합니다.")
                if not image.content_type.startswith("image/"):
                    raise serializers.ValidationError(f"{image.name}은(는) 유효한 이미지 파일이 아닙니다.")
        return value

    def create(self, validated_data):
        type_info_data = validated_data.pop("accommodationtype")
        location_info_data = validated_data.pop("gps_info")
        upload_images = validated_data.pop("upload_images", [])
        amenities_data = validated_data.pop("amenities", [])
        custom_amenities_data = validated_data.pop("custom_amenities", [])

        # 기본 숙소 생성
        accommodation = Accommodation.objects.create(**validated_data)

        # OneToOne 관계 모델 생성
        AccommodationType.objects.create(accommodation=accommodation, **type_info_data)
        GPS_Info.objects.create(accommodation=accommodation, **location_info_data)

        # 이미지 처리
        image_instances = []
        for image in upload_images:
            image_instances.append(Accommodation_Image(accommodation=accommodation, image=image))
        if image_instances:
            Accommodation_Image.objects.bulk_create(image_instances)

        # 기존 부대시설 처리
        for amenity in amenities_data:
            AccommodationAmenity.objects.create(accommodation=accommodation, amenity=amenity)

        # 커스텀 부대시설 처리
        for amenity_data in custom_amenities_data:
            amenity = Amenity.objects.create(
                name=amenity_data["name"],
                category=amenity_data.get("category", "basic"),
                description=amenity_data.get("description", ""),
                icon=amenity_data.get("icon", ""),
                is_custom=True,
            )
            AccommodationAmenity.objects.create(
                accommodation=accommodation, amenity=amenity, custom_value=amenity_data.get("custom_value", "")
            )

        return accommodation


# 업데이트용 시리얼라이저들
class AccommodationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = ["name", "phone_number", "description", "rules", "is_active"]

    def validate_phone_number(self, value):
        import re

        if not re.match(r"^\d{2,3}-\d{3,4}-\d{4}$", value):
            raise serializers.ValidationError("올바른 전화번호 형식이 아닙니다. (예: 02-123-4567 또는 010-1234-5678)")
        return value.strip()

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("숙박시설 이름은 최소 2자 이상이어야 합니다.")
        return value.strip()


class AccommodationTypeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationType
        fields = ["type_name", "is_customized"]

    def validate_type_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("숙박시설 유형은 최소 2자 이상이어야 합니다.")
        return value.strip()


class GPSInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPS_Info
        fields = ["city", "states", "road_name", "address", "location"]

    def validate(self, data):
        """GPS 정보 유효성 검사"""
        location = data.get("location")
        if location:
            coordinates = location.get("coordinates")
            if coordinates:
                try:
                    longitude, latitude = float(coordinates[0]), float(coordinates[1])
                    if not (-90 <= latitude <= 90):
                        raise serializers.ValidationError("위도는 -90에서 90 사이의 값이어야 합니다.")
                    if not (-180 <= longitude <= 180):
                        raise serializers.ValidationError("경도는 -180에서 180 사이의 값이어야 합니다.")
                    data["location"] = Point(longitude, latitude)
                except (TypeError, ValueError, IndexError):
                    raise serializers.ValidationError("유효한 위도와 경도 값을 입력해야 합니다.")

        return data


class AccommodationImageUpdateSerializer(serializers.ModelSerializer):
    """이미지 수정용 시리얼라이저"""

    class Meta:
        model = Accommodation_Image
        fields = ["image"]

    def validate_image(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("이미지 크기는 10MB를 초과할 수 없습니다.")
        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("유효한 이미지 파일이 아닙니다.")
        return value


class AccommodationAmenityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationAmenity
        fields = ["amenity", "custom_value"]

    def validate_custom_value(self, value):
        if self.instance and self.instance.amenity.is_custom and not value:
            raise serializers.ValidationError("커스텀 부대시설의 경우 상세 정보는 필수입니다.")
        return value
