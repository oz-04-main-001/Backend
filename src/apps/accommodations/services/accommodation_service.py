from apps.accommodations.models import Accommodation
from apps.rooms.models import Room


class AccommodationService:
    @staticmethod
    def get_accommodations_with_available_rooms(state, guests_count, check_in_date, check_out_date):
        """예약 가능한 숙소 목록을 반환"""

        accommodations_in_location = Accommodation.objects.filter_by_location_and_status(state)

        available_rooms = (
            Room.objects.filter_available_rooms(accommodations_in_location, guests_count)
            .annotate_overlapping_bookings(check_in_date, check_out_date)
            .filter_rooms_with_sufficient_inventory()
        )

        return Accommodation.objects.filter_by_available_rooms(available_rooms)
