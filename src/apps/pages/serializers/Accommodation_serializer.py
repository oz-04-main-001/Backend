from typing import Union

from rest_framework import serializers

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    GPS_Info,
    RefundPolicy,
)
from apps.amenities.models import AccommodationAmenity, Amenity
from apps.pages.serializers.room_serializer import RoomImagesSerializer, RoomSerializer
from apps.rooms.models import Room, Room_Image


# 호텔 주소 시리얼라이저
class AccommodationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPS_Info
        fields = [
            "city",
            "states",
            "road_name",
            "address",
        ]


# 호텔 이미지 시리얼라이저
class AccommodationImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation_Image
        fields = ["image"]


# 호텔단위 부대시설 시리얼라이저
class AccommodationAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationAmenity
        fields = "__all__"


# 호텔 환불정책
class AccommodationRefundPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundPolicy
        fields = ["seven_days_before", "five_days_before", "three_days_before", "one_day_before", "same_day"]


# 호텔 기본 정보 - 이름, 전화번호, 상세내용, 이용수칙
class AccommodationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = ["name", "phone_number", "description", "rules"]


# 숙박업소에 딸려있는 룸정보
class AccommodationRoomSerializer(serializers.ModelSerializer):
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


# ######################################
# 호텔 -> 숙소 사진, 이름, 주소, 룸최저가, 객실리스트, / 숙소소개, 편의시설, 이용규칙, 취소규정
# 룸 -> 룬사진1장 ,룸타입, 룸이름, 입실시간, 퇴실시간, 이용요금, 객실정보(기준인원, 침대싸이즈, 침대갯수, 방갯수)


class AccommodationDetailSerializer(serializers.ModelSerializer):
    accommodation_img = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()
    refund_policy = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        # 호텔 ->    숙소사진,    이름,    주소,      룸최저가,    객실리스트,           /      숙소소개,    이용규칙,  취소규정?,  편의시설,
        fields = ["accommodation_img", "name", "address", "min_price", "rooms", "description", "rules", "refund_policy"]
        # exclude = ['id', 'created_at', 'updated_at', 'is_active', 'average_rating']

    def get_accommodation_img(self, obj: Accommodation) -> Union[str, None]:
        imgs = Accommodation_Image.objects.filter(accommodation_id=obj.pk)
        if imgs:
            img_list = []
            for img in imgs:
                img_list.append(img.image.name)
            return img_list  # 이객체의 image필드의 값을 반환(클라우드 url주소 예정)

        return None  # img가 없다면 None 반환

    def get_address(self, obj):
        gps_info = GPS_Info.objects.filter(accommodation=obj)
        serializer = AccommodationAddressSerializer(gps_info, many=True)
        address_data = serializer.data[0] if serializer.data else None
        address_full = (
            f"{address_data['city']} {address_data['states']} {address_data['road_name']} {address_data['address']}"
        )
        return address_full

    def get_min_price(self, obj):
        min_price = obj.room_set.order_by("price").first()
        if min_price:
            return min_price.price
        return None

    # 룸정보 + 룸대표이미지
    def get_rooms(self, obj):
        rooms = Room.objects.filter(accommodation=obj)
        room_list = []

        for room in rooms:
            room_serializer = RoomSerializer(room)
            room_dict = room_serializer.data

            # 현재 room에 해당하는 이미지들을 가져옵니다.
            room_images = Room_Image.objects.filter(room_id=room.id)

            # 대표 이미지가 담길 변수
            representative_image = None

            # room에 대한 이미지를 순회하며 대표 이미지를 찾습니다.
            for image in room_images:
                if image.is_representative:
                    representative_image = image.image.name
                    break  # 대표 이미지를 찾으면 더 이상 순회하지 않음

            # 직렬화된 데이터에 'images' 필드로 대표 이미지를 추가
            room_dict["images"] = representative_image

            # 각 room의 데이터를 room_list에 추가
            room_list.append(room_dict)

        # room_list에는 각 room의 대표 이미지가 포함됨
        return room_list

    def get_refund_policy(self, obj):
        refund_policy = RefundPolicy.objects.filter(accommodation=obj)
        refund_policy_serializer = AccommodationRefundPolicySerializer(refund_policy, many=True)
        return refund_policy_serializer.data
