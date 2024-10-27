from typing import Optional, Union

from rest_framework import serializers

from apps.accommodations.models import Accommodation, Accommodation_Image


class MainPageSerializer(serializers.ModelSerializer):
    min_price = serializers.SerializerMethodField()
    accommodation_img = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ["id", "name", "min_price", "accommodation_img"]

    def get_min_price(self, obj: Accommodation) -> Optional[int]:
        min_price_room = obj.room_set.order_by("price").first()
        return min_price_room.price if min_price_room else None

    # 숙소 대표 이미지
    def get_accommodation_img(self, obj: Accommodation) -> Optional[Union[str, None]]:
        img = Accommodation_Image.objects.filter(accommodation=obj).get(is_representative=True)
        return img.image.url if img else None
