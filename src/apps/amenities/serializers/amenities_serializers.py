# 20241023 수정
from django.core.validators import MinLengthValidator
from rest_framework import serializers

from apps.amenities.models import AccommodationAmenity, Amenity, Option, RoomOption
from apps.common.choices import AMENITY_CHOICES


class AmenitySerializer(serializers.ModelSerializer):
    name = serializers.ChoiceField(
        choices=AMENITY_CHOICES,
        validators=[MinLengthValidator(2, "Name must be at least 2 characters long")]
    )
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Amenity
        fields = ["id", "name", "display_name", "category", "is_custom"]
        read_only_fields = ["id", "category"]  # category를 읽기 전용으로 설정
    def get_display_name(self, obj):
        """Return the human-readable name for the selected amenity"""
        return dict(AMENITY_CHOICES).get(obj.name, obj.name)

    def validate_category(self, value):
        valid_categories = ["basic", "safety", "facility", "service"]
        if value.lower() not in valid_categories:
            raise serializers.ValidationError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        return value.lower()

    #
    # def validate_icon(self, value):
    #     if value and len(value) < 3:
    #         raise serializers.ValidationError("Icon name must be at least 3 characters long")
    #     return value

    def validate_name(self, value):
        """Ensure the name is one of the valid choices unless it's a custom amenity"""
        if not self.initial_data.get('is_custom', False):
            if value not in dict(AMENITY_CHOICES):
                raise serializers.ValidationError(
                    f"Invalid amenity name. Must be one of: {', '.join(dict(AMENITY_CHOICES).keys())}"
                )
        return value

    def to_internal_value(self, data):
        if isinstance(data, list):
            return [super().to_internal_value(item) for item in data]
        else:
            return super().to_internal_value(data)

    def create(self, validated_data):
        validated_data['category'] = 'basic'
        if isinstance(validated_data, list):
            amenitie_objects = [Amenity(**data) for data in validated_data]
            return Amenity.objects.bulk_create(amenitie_objects)
        else:
            return Amenity.objects.create(**validated_data)

class AccommodationAmenitySerializer(serializers.ModelSerializer):
    """숙소 부대시설 조회용 시리얼라이저"""
    amenity = AmenitySerializer(read_only=True)
    amenity_id = serializers.PrimaryKeyRelatedField(queryset=Amenity.objects.all(), write_only=True)

    class Meta:
        model = AccommodationAmenity
        fields = ["id", "accommodation", "amenity", "amenity_id", "custom_value"]
        read_only_fields = ["custom_value"]
        # extra_kwargs = {
        #     'custom_value': {'required': False, 'allow_null': True}
        # }
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


class AccommodationAmenityListSerializer(serializers.ModelSerializer):
    """숙소 부대시설 목록 조회용 시리얼라이저"""
    amenities = AccommodationAmenitySerializer(many=True, read_only=True, source='accommodationamenity_set')

    class Meta:
        model = AccommodationAmenity
        fields = ['amenities']


# class AccommodationAmenityBulkUpdateSerializer(serializers.Serializer):
#     """숙소 부대시설 일괄 수정용 시리얼라이저"""
#     amenities = serializers.ListField(
#         child=serializers.DictField(
#             child=serializers.CharField(),
#             allow_empty=False
#         )
#     )
#
#     def validate_amenities(self, value):
#         if not value:
#             raise serializers.ValidationError("부대시설 정보는 필수입니다.")
#
#         valid_amenity_names = dict(AMENITY_CHOICES).keys()
#
#         for amenity in value:
#             if not isinstance(amenity, dict):
#                 raise serializers.ValidationError("각 부대시설은 딕셔너리 형태여야 합니다.")
#
#             # 기존 시설 수정인 경우
#             if 'id' in amenity:
#                 if not AccommodationAmenity.objects.filter(id=amenity['id']).exists():
#                     raise serializers.ValidationError(f"ID {amenity['id']}인 부대시설이 존재하지 않습니다.")
#
#             # 새로운 시설 추가인 경우
#             elif 'name' in amenity:
#                 if not amenity['name'] in valid_amenity_names and not amenity.get('is_custom', False):
#                     raise serializers.ValidationError(f"'{amenity['name']}'은(는) 유효하지 않은 부대시설입니다.")
#             else:
#                 raise serializers.ValidationError("부대시설은 id(기존 시설) 또는 name(새로운 시설)이 필요합니다.")
#
#             # custom_value 검증
#             if 'custom_value' in amenity:
#                 try:
#                     custom_value = int(amenity['custom_value'])
#                     if custom_value < 0:
#                         raise serializers.ValidationError("custom_value는 0 이상이어야 합니다.")
#                 except ValueError:
#                     raise serializers.ValidationError("custom_value는 숫자여야 합니다.")
#
#         return value
#
#     def update(self, instance, validated_data):
#         amenities_data = validated_data.get('amenities', [])
#         accommodation = instance
#
#         # 기존 부대시설 삭제
#         AccommodationAmenity.objects.filter(accommodation=accommodation).delete()
#
#         # 새로운 부대시설 생성
#         new_amenities = []
#         for amenity_data in amenities_data:
#             if 'id' in amenity_data:
#                 # 기존 어메니티 재사용
#                 amenity = Amenity.objects.get(id=amenity_data['id'])
#             else:
#                 # 새로운 어메니티 생성 또는 기존 것 찾기
#                 amenity, _ = Amenity.objects.get_or_create(
#                     name=amenity_data['name'],
#                     defaults={
#                         'category': amenity_data.get('category', 'basic'),
#                         'is_custom': amenity_data.get('is_custom', False)
#                     }
#                 )
#
#             new_amenities.append(
#                 AccommodationAmenity(
#                     accommodation=accommodation,
#                     amenity=amenity,
#                     custom_value=amenity_data.get('custom_value', None)
#                 )
#             )
#
#         # 벌크 생성
#         AccommodationAmenity.objects.bulk_create(new_amenities)
#
#         return accommodation
#


class AccommodationAmenityUpdateSerializer(serializers.ModelSerializer):
    """숙소 부대시설 수정용 시리얼라이저"""
    amenities = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
    )

    class Meta:
        model = AccommodationAmenity
        fields = ["amenities"]  # name 필드 추가

    def validate_amenities(self, value):
        if not value:
            raise serializers.ValidationError("부대시설 정보는 필수입니다.")

        for amenity in value:
            if isinstance(amenity, dict):
                if "id" not in amenity and "name" not in amenity:
                    raise serializers.ValidationError("부대시설은 id(기존 시설) 또는 name(새로운 시설)이 필요합니다.")
            elif not isinstance(amenity, (int, str)):
                raise serializers.ValidationError("잘못된 부대시설 데이터 형식입니다.")

        return value

    def update(self, instance, validated_data):
        amenities_data = validated_data.get('amenities', [])

        # 기존 부대시설 삭제
        AccommodationAmenity.objects.filter(accommodation=instance.accommodation).delete()

        # 새로운 부대시설 생성
        new_amenities = []
        for amenity_data in amenities_data:
            if isinstance(amenity_data, dict):
                if 'id' in amenity_data:
                    # 기존 어메니티 재사용
                    try:
                        amenity = Amenity.objects.get(id=amenity_data['id'])
                    except Amenity.DoesNotExist:
                        raise serializers.ValidationError(f"Amenity with id {amenity_data['id']} does not exist")
                else:
                    # 새로운 어메니티 생성 또는 기존 것 찾기
                    amenity, _ = Amenity.objects.get_or_create(
                        name=amenity_data['name'],
                        defaults={
                            'category': amenity_data.get('category', 'basic'),
                            'is_custom': amenity_data.get('is_custom', False)
                        }
                    )

                custom_value = amenity_data.get('custom_value') if amenity.is_custom else None
                new_amenities.append(
                    AccommodationAmenity(
                        accommodation=instance.accommodation,
                        amenity=amenity,
                        custom_value=custom_value
                    )
                )

        # 벌크 생성
        if new_amenities:
            AccommodationAmenity.objects.bulk_create(new_amenities)

        return instance


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


class RoomOptionUpdateSerializer(serializers.ModelSerializer):
    option = OptionSerializer(read_only=True)
    option_id = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(), write_only=True, required=False)

    class Meta:
        model = RoomOption
        fields = ["id", "room", "option", "option_id", "custom_value"]

    def validate(self, data):
        option = data.get("option_id")
        custom_value = data.get("custom_value", "")

        if option and option.is_custom and not custom_value:
            raise serializers.ValidationError({"custom_value": "Custom value is required for custom options"})

        if option and not option.is_custom and custom_value:
            raise serializers.ValidationError({"custom_value": "Custom value should not be set for non-custom options"})

        return data

    def update(self, instance, validated_data):
        option = validated_data.get("option_id", instance.option)
        custom_value = validated_data.get("custom_value", instance.custom_value)

        # 옵션 및 custom_value 업데이트
        instance.option = option
        instance.custom_value = custom_value
        instance.save()

        return instance
