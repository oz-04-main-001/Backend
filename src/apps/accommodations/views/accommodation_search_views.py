from django.contrib.gis.measure import D
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_gis.filters import DistanceToPointFilter
from rest_framework_gis.pagination import GeoJsonPagination

from apps.accommodations.models import Accommodation
from apps.accommodations.serializers.accommodations_search_serializer import (
    AccommodationAvailabilityRequestSerializer,
    AccommodationAvailabilityResponseSerializer,
    KakaoPlaceDataSerializer,
)
from apps.accommodations.services.accommodation_service import AccommodationService
from apps.accommodations.services.geocoding_service import GeocodingService
from apps.common.choices import CITY_COORDINATES


@extend_schema(tags=["Guest-Search"])
class AvailableAccommodationsAPIView(GenericAPIView):
    serializer_class = AccommodationAvailabilityRequestSerializer
    geocoding_service = GeocodingService()
    queryset = Accommodation.objects.select_related("gps_info")

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
                name="guests_count",
                description="Number of guests for the booking",
                required=True,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name="city",
                description="City or region where the accommodation is located",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="point",
                description="Coordinates for the location in 'longitude,latitude' format, e.g., '126.978,37.5665'",
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample(
                        name="sample_point",
                        summary="Example coordinates for the point parameter",
                        description="Coordinates in 'longitude,latitude' format.",
                        value="126.978,37.5665",  # Example: 서울의 경도와 위도
                    )
                ],
            ),
            OpenApiParameter(
                name="dist",
                description="Search radius in meters (e.g., 5000 for 5 km)",
                required=False,
                type=OpenApiTypes.INT,
            ),
        ],
        summary="검색 결과 숙소 조회 API",
    )
    def get(self, request, *args, **kwargs):
        """
        query_params: check_in_date, check_out_date, state, guests_count \n\n
        return: list of accommodations with available rooms \n\n
        필수 입력값\n\n
        check_in_date: YYYY-MM-DD \n\n
        check_out_date: YYYY-MM-DD \n\n
        guests_count: int \n\n
        \n\n
        선택 입력값\n\n
        검색으로 사용 시 city, 지도로 사용시 point 입력\n\n
        city: '서울특별시' \n\n
        point: '126.978,37.5665' \n\n
        dist: 5000 (반경 5km default)\n\n
        """
        coordinates = request.query_params.get("point")
        serializer = self.get_serializer(data=request.query_params, context={"coordinates": coordinates})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        check_in_date = validated_data["check_in_date"]
        check_out_date = validated_data["check_out_date"]
        guests_count = validated_data["guests_count"]
        city = validated_data.get("city", "")
        location = validated_data.get("location", "")
        radius = validated_data.get("dist", 5000)

        filtered_accommodations = AccommodationService.get_accommodations_with_available_rooms(
            city=city,
            location=location,
            radius=radius,
            guests_count=guests_count,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
        )

        if location:
            latitude, longitude = location.coords
        else:
            latitude, longitude = CITY_COORDINATES[city]

        kakao_place_data = self.geocoding_service.search_accommodations_and_images(
            latitude=latitude, longitude=longitude
        )

        accommodation_serializer = AccommodationAvailabilityResponseSerializer(filtered_accommodations, many=True)

        kakao_place_data_serializer = KakaoPlaceDataSerializer(kakao_place_data, many=True)

        combined_data = {
            "accommodation_data": accommodation_serializer.data,
            "kakao_place_data": kakao_place_data_serializer.data,
        }

        return Response(combined_data, status=status.HTTP_200_OK)
