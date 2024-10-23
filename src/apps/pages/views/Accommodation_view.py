from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.accommodations.models import Accommodation
from apps.pages.serializers.Accommodation_serializer import AccommodationDetailSerializer


@extend_schema(tags=["Guest"])
class AccommodationDetailView(RetrieveAPIView):
    serializer_class = AccommodationDetailSerializer
    permission_classes = (AllowAny,)
    queryset = Accommodation.objects.all()

    @extend_schema(
        summary="  >> 숙박 업소 디테일 페이지 / {accommodation_id}<<",
        description="capacity:기준 인원 / max_capacity:최대 인원 ",
        responses = {200:AccommodationDetailSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
