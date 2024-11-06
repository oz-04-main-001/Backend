from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.serializers import as_serializer_error
from rest_framework_gis.fields import GeometryField

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    AccommodationType,
    GPS_Info,
    RefundPolicy,
)
from apps.amenities.models import AccommodationAmenity, Amenity
from apps.amenities.serializers.amenities_serializers import (
    AccommodationAmenityUpdateSerializer,
)
from apps.common.choices import ACCOMMODATION_TYPE_CHOICES


# 기본 조회/생성용 시리얼라이저들
class GPSInfoSerializer(serializers.ModelSerializer):
    location = GeometryField()

    class Meta:
        model = GPS_Info
        fields = ["city", "states", "road_name", "address", "location"]

    def validate(self, data):
        """GPS 정보 유효성 검사"""
        location = data.get("location")
        if location:
            try:
                # Point 객체인 경우
                if isinstance(location, Point):
                    longitude, latitude = location.x, location.y
                # GeoJSON 형식으로 들어온 경우
                elif isinstance(location, dict) and "coordinates" in location:
                    longitude, latitude = location["coordinates"]
                else:
                    raise serializers.ValidationError("잘못된 위치 데이터 형식입니다.")

                if not (-90 <= latitude <= 90):
                    raise serializers.ValidationError("위도는 -90에서 90 사이의 값이어야 합니다.")
                if not (-180 <= longitude <= 180):
                    raise serializers.ValidationError("경도는 -180에서 180 사이의 값이어야 합니다.")

                # 이미 Point 객체가 아닌 경우에만 새로 생성
                if not isinstance(location, Point):
                    data["location"] = Point(longitude, latitude)

            except (TypeError, ValueError, IndexError, KeyError):
                raise serializers.ValidationError("유효한 위도와 경도 값을 입력해야 합니다.")
        else:
            raise serializers.ValidationError("위치 정보가 필요합니다.")

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
        read_only_fields = ["is_customized"]
        extra_kwargs = {
            "type_name": {"default": "호텔"},
            # 'is_customized': {'default': False},# is_customized 필드를 옵션으로 설정
        }

    def validate(self, data):
        type_name = data.get("type_name", "")  # 소문자로 변환
        data["type_name"] = type_name  # 변환된 값을 다시 저장
        is_customized = data.get("is_customized", False)
        valid_types = [choice[0] for choice in ACCOMMODATION_TYPE_CHOICES]

        if not is_customized and type_name not in valid_types:
            raise serializers.ValidationError(
                f"'{type_name}'은(는) 기본 숙소 유형이 아닙니다. 다음 중 하나를 선택하세요: {', '.join(valid_types)}"
                f" 또는 커스텀 타입으로 설정하려면 is_customized를 true로 설정하세요."
            )

        return data

    def create(self, validated_data):
        validated_data["is_customized"] = False
        return AccommodationType.objects.create(**validated_data)

        # 커스텀 타입인 경우 새로 생성
        # return AccommodationType.objects.create(**validated_data)


class AccommodationImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(
        use_url=True,
        required=True,
        allow_empty_file=True,
        error_messages={
            "invalid": "유효한 이미지 파일이 아닙니다.",
            "empty": "이미지 파일이 비어있습니다.",
            "invalid_image": "올바른 이미지 파일 형식이 아닙니다.",
        },
    )

    class Meta:
        model = Accommodation_Image
        fields = ["id", "accommodation", "image", "image_url"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def validate_image(self, value):
        if value:
            if value.size > 10 * 1024 * 1024:  # 10MB
                raise serializers.ValidationError("이미지 크기가 10MB를 초과할 수 없습니다.")
            # if not value.content_type.startswith("image/"):
            #     raise serializers.ValidationError("유효한 이미지 파일이 아닙니다.")
        return value

    # def run_validation(self, data=empty):
    #     (is_empty_value, data) = self.validate_empty_values(data)
    #     if is_empty_value:
    #         return data
    #
    #     value = self.to_internal_value(data)
    #     try:
    #         if isinstance(value, dict):
    #             self.run_validators(value)
    #             value = self.validate(value)
    #         elif isinstance(value, list):
    #             for item in value:
    #                 self.run_validators(item)
    #             value = [self.run_validators(item) for item in value]
    #         assert value is not None, '.validate() should return the validated data'
    #     except (ValidationError, DjangoValidationError) as exc:
    #         raise ValidationError(detail=as_serializer_error(exc))
    #
    #     return value
    #
    # def to_internal_value(self, data):
    #     if isinstance(data, list):
    #         return [super().to_internal_value(item) for item in data]
    #     else:
    #         return super().to_internal_value(data)
    #
    # def create(self, validated_data):
    #     if isinstance(validated_data, list):
    #         image_objects = [Accommodation_Image(**data) for data in validated_data]
    #         return Accommodation_Image.objects.bulk_create(image_objects)
    #     else:
    #         return Accommodation_Image.objects.create(**validated_data)

    # def create(self, validated_data):
    #     image_instances = [Accommodation_Image(
    #             accommodation_id=validated_data.get("accommodation"),
    #             image=image) for image in validated_data.get("images")]
    #     return Accommodation_Image.objects.bulk_create(image_instances)


class RefundPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundPolicy
        fields = ["seven_days_before", "five_days_before", "three_days_before", "one_day_before", "same_day"]
        extra_kwargs = {
            "seven_days_before": {"required": True},
            "five_days_before": {"required": True},
            "three_days_before": {"required": True},
            "one_day_before": {"required": True},
            "same_day": {"required": True},
        }

    def validate(self, data):
        for field, value in data.items():
            if value < 0 or value > 100:
                raise serializers.ValidationError(f"{field}: 환불 비율은 0에서 100 사이여야 합니다.")
        return data


class AccommodationSerializer(serializers.ModelSerializer):
    host = serializers.PrimaryKeyRelatedField(read_only=True)
    phone_number = serializers.CharField(read_only=True)

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
        ]
        read_only_fields = ["id", "average_rating", "created_at", "updated_at", "phone_number"]

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

    def create(self, validated_data):
        # host는 view에서 전달받음
        instance = super().create(validated_data)
        # host의 전화번호 설정
        if hasattr(instance.host, "phone_number"):
            instance.phone_number = instance.host.phone_number
        elif hasattr(instance.host.user, "phone_number"):
            instance.phone_number = instance.host.user.phone_number
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # phone_number는 update에서 제외
        if "phone_number" in validated_data:
            del validated_data["phone_number"]

        instance = super().update(instance, validated_data)

        # host의 전화번호로 업데이트
        if hasattr(instance.host, "phone_number"):
            instance.phone_number = instance.host.phone_number
        elif hasattr(instance.host.user, "phone_number"):
            instance.phone_number = instance.host.user.phone_number
        instance.save()
        return instance


# 업데이트용 시리얼라이저들
class AccommodationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = ["name", "phone_number", "description", "rules", "is_active"]
        read_only_fields = ["phone_number"]

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
