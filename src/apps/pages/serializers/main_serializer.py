from typing import Optional

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

    def get_accommodation_img(self, obj: Accommodation) -> Optional[str]:
        # Accommodation과 연결된 Accommodation_Image 테이블에서 첫 번째 이미지의 URL을 반환
        img = Accommodation_Image.objects.filter(accommodation_id=obj.pk).first()
        return img.image.url if img else None
