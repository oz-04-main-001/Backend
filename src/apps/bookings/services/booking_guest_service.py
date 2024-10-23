from apps.bookings.models import Booking
from apps.users.models import User


class BookingService:
    def create_booking(self, data: dict, user: User):

        self._check_booker_data(data, user)

        booking = Booking.objects.create(
            guest=data["guest"],
            check_in_date=data["check_in_date"],
            check_out_date=data["check_out_date"],
            guests_count=data["guests_count"],
            booker_name=data["booker_name"],
            booker_phone_number=data["booker_phone_number"],
            room_id=data["room_id"],
            total_price=data["total_price"],
        )
        return booking

    @staticmethod
    def _check_booker_data(data, user):
        if not data.get("booker_phone_number") or data.get("booker_phone_number"):
            data["booker_phone_number"] = user.phone_number
            data["booker_name"] = user.name
            data["guest"] = user

    @staticmethod
    def check_overlapping_bookings(room, check_in_date, check_out_date):
        return Booking.objects.overlapping(room, check_in_date, check_out_date)
