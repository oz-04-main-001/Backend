from django.db.models.functions import Coalesce
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, F

from apps.accommodations.models import Accommodation, GPS_Info
from apps.accommodations.serializers.accommodations_search_serializer import (
    AccommodationAvailabilityRequestSerializer,
    AccommodationAvailabilityResponseSerializer,
)
from apps.rooms.models import Room


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
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        state = validated_data["state"]
        check_in_date = validated_data["check_in_date"]
        check_out_date = validated_data["check_out_date"]
        guests_count = validated_data["guests_count"]

        accommodations_in_location = Accommodation.objects.filter(Q(gps_info__states=state) & Q(is_active=True))

        available_rooms = (
            Room.objects.filter(
                Q(accommodation__in=accommodations_in_location)
                & Q(capacity__lte=guests_count)
                & Q(max_capacity__gte=guests_count)
                & Q(is_available=True)
            )
            .annotate(
                overlapping_bookings=Coalesce(
                    Count(
                        "booking",
                        filter=Q(
                            booking__check_out_datetime__gt=check_in_date, booking__check_in_datetime__lt=check_out_date
                        ),
                    ),
                    0,
                )
            )
            .filter(roominventory__count_room__gt=F("overlapping_bookings"))
        )

        accommodations_with_available_rooms = Accommodation.objects.filter(Q(room__in=available_rooms)).distinct()

        response_serializer = AccommodationAvailabilityResponseSerializer(
            accommodations_with_available_rooms, many=True
        )

        return Response(response_serializer.data, status=status.HTTP_200_OK)
