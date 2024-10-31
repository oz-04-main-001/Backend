from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accommodations.services.accommodation_service import AccommodationService
from apps.pages.serializers.accommodation_serializer import (
    AccommodationRequestSerializer,
    AccommodationResponseSerializer,
)


# 숙박 업소 디테일 뷰
@extend_schema(tags=["Guest"])
class AccommodationDetailView(GenericAPIView):
    serializer_class = AccommodationRequestSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        request=AccommodationRequestSerializer,
        responses={200: AccommodationResponseSerializer(many=True)},
        summary="숙박 업소 디테일",
        description="capacity: 기준 인원 / max_capacity: 최대 인원",
        parameters=[
            OpenApiParameter(
                name="check_in_date",
                description="Check-in date for the booking (YYYY-MM-DD)",
                required=True,
                type=OpenApiTypes.DATE,
            ),
            OpenApiParameter(
                name="check_out_date",
                description="Check-out date for the booking (YYYY-MM-DD)",
                required=True,
                type=OpenApiTypes.DATE,
            ),
            OpenApiParameter(
                name="guests_count",
                description="Number of guests for the booking",
                required=True,
                type=OpenApiTypes.INT,
            ),
        ],
    )
    def get(self, request: Request, accommodation_id: int, *args, **kwargs):

        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        check_in_date = validated_data["check_in_date"]
        check_out_date = validated_data["check_out_date"]
        guests_count = validated_data["guests_count"]

        accommodation_data = AccommodationService.get_accommodation_detail_with_available_rooms(
            accommodation_id=accommodation_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            guests_count=guests_count,
        )

        serializer = AccommodationResponseSerializer(accommodation_data)

        return Response(serializer.data, status=status.HTTP_200_OK)
