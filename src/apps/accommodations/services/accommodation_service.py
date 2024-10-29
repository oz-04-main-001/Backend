from apps.accommodations.models import Accommodation
from apps.common.choices import POSSIBLE_CITY
from apps.rooms.models import Room


class AccommodationService:
    @staticmethod
    def get_accommodations_with_available_rooms(city, guests_count, check_in_date, check_out_date):
        """예약 가능한 숙소 목록을 반환"""
        city_variants = POSSIBLE_CITY.get(city, [city])

        accommodations_in_location = Accommodation.objects.filter_by_location_and_status(city=city_variants)

        available_rooms = (
            Room.objects.filter_available_rooms(accommodations_in_location, guests_count)
            .annotate_overlapping_bookings(check_in_date, check_out_date)
            .filter_rooms_with_sufficient_inventory()
        )

        return Accommodation.objects.filter_by_available_rooms(available_rooms)

    @staticmethod
    def get_accommodation_detail_with_available_rooms(accommodation_id, guests_count, check_in_date, check_out_date):
        """특정 숙소의 예약 가능한 방 목록 반환"""

        # 지정된 ID로 숙소 조회
        accommodation = Accommodation.objects.filter(id=accommodation_id, is_active=True).first()

        all_rooms = Room.objects.filter(accommodation=accommodation)

        available_rooms = (
            all_rooms.filter_available_room(accommodation, guests_count)
            .annotate_overlapping_bookings(check_in_date, check_out_date)
            .filter_rooms_with_sufficient_inventory()
        )

        unavailable_rooms = all_rooms.exclude(id__in=available_rooms.values_list("id", flat=True))

        accommodation_data = {
            "accommodation": accommodation,  # Accommodation 객체
            "available_rooms": available_rooms,  # 예약 가능한 Room 쿼리셋
            "unavailable_rooms": unavailable_rooms,  # 예약 불가능한 Room 쿼리셋
        }

        return accommodation_data
