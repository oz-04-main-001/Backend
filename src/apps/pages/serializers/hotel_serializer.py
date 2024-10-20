from typing import Union

from rest_framework import serializers

from apps.accommodations.models import Accommodation, Accommodation_Image, GPS_Info
from apps.amenities.models import AccommodationAmenity, Amenity
from apps.pages.serializers.room_serializer import RoomSerializer
from apps.rooms.models import Room


# 호텔 주소 시리얼라이저
class HotelAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPS_Info
        fields = [
            "city",
            "states",
            "road_name",
            "address",
        ]


# 호텔 이미지 시리얼라이저
class HotelImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation_Image
        fields = ["image"]


# 호텔단위 부대시설 시리얼라이저
class HotelAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationAmenity
        fields = "__all__"


# 호텔 기본 정보 - 이름, 전화번호, 상세내용, 이용수칙(환불규정?)
class HotelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = ["name", "phone_number", "description", "rules"]


# ######################################
# 호텔 -> 숙소 사진, 이름, 주소, 룸최저가, 객실리스트, / 숙소소개, 편의시설, 이용규칙, 취소규정
# 룸 -> 룬사진1장 ,룸타입, 룸이름, 입실시간, 퇴실시간, 이용요금, 객실정보(기준인원, 침대싸이즈, 침대갯수, 방갯수)


class HotelDetailSerializer(serializers.ModelSerializer):
    hotel_img = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()
    # hotel_amenities = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        # 호텔 ->    숙소사진,    이름,    주소,      룸최저가,    객실리스트,           /      숙소소개,    이용규칙,  취소규정?,  편의시설,
        fields = ["hotel_img", "name", "address", "min_price", "rooms", "phone_number", "description", "rules", "host"]
        # exclude = ['id', 'created_at', 'updated_at', 'is_active', 'average_rating']

    def get_hotel_img(self, obj: Accommodation) -> Union[str, None]:
        imgs = Accommodation_Image.objects.filter(accommodation_id=obj.pk)
        if imgs:
            img_list = []
            for img in imgs:
                img_list.append(img.image.name)
            return img_list  # 이객체의 image필드의 값을 반환(클라우드 url주소 예정)

        return None  # img가 없다면 None 반환

    def get_address(self, obj):
        gps_info = GPS_Info.objects.filter(accommodation=obj)
        serializer = HotelAddressSerializer(gps_info, many=True)
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

    def get_rooms(self, obj):
        rooms = Room.objects.filter(accommodation=obj)
        serializer = RoomSerializer(rooms, many=True)
        return serializer.data

    # def get_hotel_amenities(self, obj):
    #     hotel_amenities = Amenity.objects.filter(accommodationamenity=obj)
    #     serializer = HotelAmenitySerializer(hotel_amenities, many=True)
    #     return serializer.data
