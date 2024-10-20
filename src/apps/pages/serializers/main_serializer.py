from typing import Union

from apps.accommodations.models import Accommodation, Accommodation_Image
from rest_framework import serializers


class MainPageSerializer(serializers.ModelSerializer):
    rooms = serializers.SerializerMethodField()
    hotel_img = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ["name", "rooms", "hotel_img"]

    def get_rooms(self, obj: Accommodation) -> Union[int, None]:
        min_price_room = obj.room_set.order_by("price").first()
        if min_price_room:
            return min_price_room.price
        return None

    def get_hotel_img(self, obj: Accommodation) -> Union[str, None]:
        # Accommodation과 연결된 Accommodation_image 테이블에서 첫 번째 이미지의 URL을 반환
        img = Accommodation_Image.objects.filter(accommodation_id=obj.pk).first()  # 이미지들중 첫번째 이미지
        if img:  # img가 있다면
            return (img.image.name)  # 이객체의 image필드의 값을 반환(클라우드 url주소 예정)

        return None  # img가 없다면 None 반환
