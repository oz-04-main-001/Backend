from typing import Optional, Union

from rest_framework import serializers

from apps.accommodations.models import Accommodation, Accommodation_Image
from apps.pages.services.money_view_service import MoneyViewService


class MainPageSerializer(serializers.ModelSerializer):
    min_price = serializers.SerializerMethodField()
    accommodation_img = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ["id", "name", "min_price", "accommodation_img"]

    def get_min_price(self, obj: Accommodation) -> Optional[int]:
        min_price_room = obj.room_set.order_by("price").first()
        if min_price_room is not None:
            money_mark = MoneyViewService()
            money_min_price = money_mark.format(min_price_room.price)
            return money_min_price
        return None  # 방이 없는 경우 None 반환

    # 숙소 대표 이미지
    def get_accommodation_img(self, obj: Accommodation) -> Optional[Union[str, None]]:
        img = Accommodation_Image.objects.filter(accommodation=obj).filter(is_representative=True).first()
        return img.image.url if img else None
