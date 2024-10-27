from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.accommodations.models import Accommodation
from apps.pages.serializers.main_serializer import MainPageSerializer


# /api/v1/ui/main/
@extend_schema(tags=["Guest"])
class MainListView(ListAPIView):
    serializer_class = MainPageSerializer
    permission_classes = (AllowAny,)
    queryset = Accommodation.objects.all().order_by("?")

    # 보류
    # pagination_class = MainListPagination

    @extend_schema(
        summary="첫 화면 - 랜덤 숙소 - 누구나 /",
        description="min_price : 룸 최저 가격 / accommodation_img : 숙소 대표 이미지",
        responses={200: MainPageSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
