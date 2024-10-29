from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.accommodations.serializers.accommodations_search_serializer import (
    AccommodationAvailabilityRequestSerializer,
    AccommodationAvailabilityResponseSerializer,
)
from apps.accommodations.services.accommodation_service import AccommodationService
from apps.accommodations.services.geocoding_service import GeocodingService
from apps.common.choices import STATE_COORDINATES


@extend_schema(tags=["Guest-Search"])
class AvailableAccommodationsAPIView(GenericAPIView):
    serializer_class = AccommodationAvailabilityRequestSerializer

    @extend_schema(
        request=AccommodationAvailabilityRequestSerializer,
        responses={status.HTTP_200_OK: AccommodationAvailabilityResponseSerializer(many=True)},
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
                name="state",
                description="State or region where the accommodation is located",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="guests_count",
                description="Number of guests for the booking",
                required=True,
                type=OpenApiTypes.INT,
            ),
        ],
        summary="검색 결과 숙소 조회 API",
    )
    def get(self, request, *args, **kwargs):
        """
        query_params: check_in_date, check_out_date, state, guests_count \n\n
        return: list of accommodations with available rooms \n\n
        check_in_date: YYYY-MM-DD \n\n
        check_out_date: YYYY-MM-DD \n\n
        state: '서울특별시' \n\n
        guests_count: int \n\n
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        state = validated_data["state"]
        check_in_date = validated_data["check_in_date"]
        check_out_date = validated_data["check_out_date"]
        guests_count = validated_data["guests_count"]

        accommodations_with_available_rooms = AccommodationService.get_accommodations_with_available_rooms(
            state=state, guests_count=guests_count, check_in_date=check_in_date, check_out_date=check_out_date
        )

        latitude, longitude = STATE_COORDINATES[state]

        kakao_place = GeocodingService.search_accommodations(latitude=latitude, longitude=longitude)
        print(kakao_place)

        response_serializer = AccommodationAvailabilityResponseSerializer(
            accommodations_with_available_rooms, many=True
        )

        return Response(response_serializer.data, status=status.HTTP_200_OK)
