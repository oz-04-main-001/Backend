from apps.bookings.models import Booking
from apps.users.models import User


class BookingService:
    @staticmethod
    def create_booking(data: dict, user: User):
        booking = Booking.objects.create(
            guest=user,
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
    def check_booker_data(data: dict, user: User) -> dict:
        if not data.get("booker_phone_number") or data.get("booker_phone_number"):
            data["booker_phone_number"] = user.phone_number
            data["booker_name"] = user.name
        return data

    @staticmethod
    def check_overlapping_bookings(room, check_in_date, check_out_date):
        return Booking.objects.overlapping(room, check_in_date, check_out_date)

    @staticmethod
    def cancel_booking(booking_id: str):
        booking = Booking.objects.get_by_booking_id(booking_id=booking_id)

        if booking is None:
            raise Booking.DoesNotExist("Booking not found.")

        booking.status = "cancelled_by_guest"
        booking.save()
        return booking
