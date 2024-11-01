# room_serializer.py
import json

from django.utils import timezone
from rest_framework import serializers

from apps import accommodations
from apps.accommodations.models import AccommodationType
from apps.amenities.models import Option, RoomOption
from apps.amenities.serializers.amenities_serializers import OptionSerializer
from apps.common.choices import BED_TYPE_CHOICES, ROOM_TYPE_CHOICES
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ["is_customized", "type_name"]  # room 필드 제거
        extra_kwargs = {
            "type_name": {"required": False},
            "is_customized": {"default": False},  # 커스텀 타입 허용
        }

    def validate(self, data):
        type_name = data.get("type_name", "").lower()
        data["type_name"] = type_name
        is_customized = data.get("is_customized", False)
        valid_types = [choice[0] for choice in ROOM_TYPE_CHOICES]

        room_data = self.context.get("request").data.get("room")
        accommodation_id = json.loads(room_data).get("accommodation")
        accommodation_type = AccommodationType.objects.get(accommodation_id=accommodation_id)

        if "독채" not in accommodation_type.type_name:
            if not is_customized and type_name not in valid_types:
                raise serializers.ValidationError(
                    f"'{type_name}'은(는) 유효한 방 유형이 아닙니다. "
                    f"다음 중 하나를 선택하세요: {', '.join(valid_types)}"
                    f" 또는 커스텀 타입으로 설정하려면 is_customized를 true로 설정하세요."
                )

        return data


class RoomImageSerializer(serializers.ModelSerializer):
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
        model = Room_Image
        fields = ["id", "room", "image", "image_url"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def validate_image(self, value):
        if value:
            if value.size > 10 * 1024 * 1024:  # 10MB
                raise serializers.ValidationError("이미지 크기가 10MB를 초과할 수 없습니다.")
        elif not value.get("upload_images"):
            raise serializers.ValidationError({"upload_images": "At least one image is required"})

        return value


class RoomInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInventory
        fields = ["count_room"]
        extra_kwargs = {"count_room": {"default": 1, "min_value": 1, "help_text": "방의 총 개수"}}  # 최소값 1 설정

    def validate_count_room(self, value):
        if value < 1:  # 0도 허용하지 않음
            raise serializers.ValidationError("방 개수는 최소 1개 이상이어야 합니다.")
        if value > 100:  # 적절한 최대값 설정
            raise serializers.ValidationError("방 개수가 너무 많습니다. (최대 100개)")
        return value


class RoomSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = ["id", "stay_type", "max_capacity"]
        extra_kwargs = {
            "capacity": {"default": 2},
            "accommodation": {"default": 1},
            "price": {"default": 50000},
            "check_in_time": {"default": "15:00:00"},
            "check_out_time": {"default": "11:00:00"},
            "is_available": {"default": True},
        }

    def validate(self, data):
        # 기존 validation
        if not data.get("capacity"):
            raise serializers.ValidationError({"capacity": "Capacity is required"})

        if not data.get("price"):
            raise serializers.ValidationError({"price": "Price is required"})

        if not data.get("name"):
            raise serializers.ValidationError({"name": "Name is required"})

        if data["capacity"] <= 0:
            raise serializers.ValidationError({"capacity": "Capacity must be greater than 0"})

        if data["price"] <= 0:
            raise serializers.ValidationError({"price": "Price must be greater than 0"})

        check_in = data.get("check_in_time")
        check_out = data.get("check_out_time")
        stay_type = data.get("stay_type")
        if check_in and check_out:
            if stay_type == False:  # 대실일 경우
                if check_in >= check_out:  # 대실은 체크아웃이 체크인보다 빨라야 함
                    raise serializers.ValidationError(
                        {"check_in_time": "대실의 경우 체크아웃 시간이 체크인 시간보다 빨라야 합니다."}
                    )

            else:  # 숙박일 경우
                if check_in <= check_out:  # 숙박은 체크인이 체크아웃보다 빨라야 함
                    raise serializers.ValidationError(
                        {"check_in_time": "숙박의 경우 체크인 시간이 체크아웃 시간보다 빨라야 합니다."}
                    )
        if len(data["name"]) < 2:
            raise serializers.ValidationError({"name": "Room name must be at least 2 characters long"})

        # 이미지 validation

        return data

    def create(self, validated_data):
        validated_data["stay_type"] = True
        validated_data["max_capacity"] = 1000
        instance = super().create(validated_data)
        # getattr를 사용하여 더 안전하게 처리
        instance.accommodation_name = getattr(instance.accommodation, "name", None)
        instance.save()
        return instance  # 1. Room 생성

    def update(self, instance, validated_data):
        validated_data.pop("accommodation", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.accommodation_name = getattr(instance.accommodation, "name", None)
        instance.save()
        return instance


# room_serializer.py에 추가
class RoomUpdateSerializer(serializers.ModelSerializer):
    """Room 기본 정보 수정용 시리얼라이저"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:  # update 시에만 실행
            # 기존 값을 default로 설정
            self.fields["name"].default = self.instance.name
            self.fields["description"].default = self.instance.description

    class Meta:
        model = Room
        fields = [
            "name",
            "capacity",
            "max_capacity",
            "price",
            "stay_type",
            "description",
            "check_in_time",
            "check_out_time",
            "is_available",
        ]
        read_only_fields = ["id", "stay_type", "max_capacity"]
        extra_kwargs = {
            "capacity": {"default": 2},
            "price": {"default": 50000},
            "check_in_time": {"default": "15:00:00"},
            "check_out_time": {"default": "11:00:00"},
            "is_available": {"default": True},
        }

    def validate(self, data):
        # capacity validation
        if "capacity" in data and "max_capacity" in data:
            if data["capacity"] > data["max_capacity"]:
                raise serializers.ValidationError({"capacity": "Capacity cannot be greater than max capacity"})
            if data["capacity"] <= 0:
                raise serializers.ValidationError({"capacity": "Capacity must be greater than 0"})

        # price validation
        if "price" in data and data["price"] <= 0:
            raise serializers.ValidationError({"price": "Price must be greater than 0"})

        # check-in/out time validation
        check_in = data.get("check_in_time")
        check_out = data.get("check_out_time")
        if check_in and check_out and check_in <= check_out:
            raise serializers.ValidationError({"check_in_time": "Check-in time must be after check-out time"})

        # name validation
        if "name" in data and len(data["name"]) < 2:
            raise serializers.ValidationError({"name": "Room name must be at least 2 characters long"})

        return data

    def update(self, instance, validated_data):
        validated_data["max_capacity"] = 1000
        accommodation_type = AccommodationType.objects.get(accommodation=instance.accommodation)
        if "독채" in accommodation_type.type_name:
            # 독채인 경우 항상 accommodation의 name과 description으로 설정
            validated_data["name"] = instance.accommodation.name
            validated_data["description"] = instance.accommodation.description

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BedOptionSerializer(serializers.ModelSerializer):
    bed_type = serializers.ChoiceField(choices=BED_TYPE_CHOICES, source="name")
    quantity = serializers.IntegerField(min_value=0, required=True, write_only=True)

    class Meta:
        model = Option
        fields = ["id", "bed_type", "quantity"]

    def validate(self, data):
        bed_type = data.get("name")
        quantity = data.get("quantity", 0)

        if bed_type == "none":
            # 침대가 없는 경우 수량을 0으로 강제
            data["quantity"] = 0
        elif quantity < 0:
            # 침대가 있는데 수량이 음수인 경우
            raise serializers.ValidationError("침대 수량은 0보다 작을 수 없습니다.")
        elif quantity == 0:
            # 침대 타입을 선택했는데 수량이 0인 경우
            raise serializers.ValidationError("침대 타입을 선택한 경우 최소 1개 이상이어야 합니다.")

        return data

    def to_representation(self, instance):
        """응답 데이터에 quantity 포함"""
        data = super().to_representation(instance)
        data["quantity"] = self.context.get("quantity", 0)  # context에서 quantity 값을 가져옴
        return data


class RoomBedOptionsSerializer(serializers.ModelSerializer):
    bed_options = BedOptionSerializer(many=True, write_only=True)

    class Meta:
        model = Room
        fields = ["bed_options"]

    def update(self, instance, validated_data):
        bed_options_data = validated_data.get("bed_options", [])

        # 기존 침대 옵션들을 모두 삭제
        RoomOption.objects.filter(room=instance, option__category="bed").delete()

        # 새로운 침대 옵션들을 생성
        new_options = []

        for bed_option in bed_options_data:
            bed_type = bed_option["bed_type"]
            quantity = bed_option["quantity"]

            # none이 아니고 수량이 있는 경우에만 생성
            if bed_type != "none" and quantity > 0:
                option, _ = Option.objects.get_or_create(name=bed_type, category="bed", defaults={"is_custom": False})

                new_options.append(RoomOption(room=instance, option=option, custom_value=str(quantity)))

        if new_options:
            RoomOption.objects.bulk_create(new_options)

        return instance

    def to_representation(self, instance):
        bed_options = []
        room_options = RoomOption.objects.filter(room=instance, option__category="bed").select_related("option")

        # 현재 설정된 침대 옵션들을 변환
        for room_option in room_options:
            bed_options.append({"bed_type": room_option.option.name, "quantity": int(room_option.custom_value or 0)})

        # 설정된 옵션이 없으면 "none" 타입 반환
        if not bed_options:
            bed_options.append({"bed_type": "none", "quantity": 0})

        return {"bed_options": bed_options}
