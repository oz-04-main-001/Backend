from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class BookingQuerySet(models.QuerySet):
    def overlapping(self, room, check_in_datetime, check_out_datetime):
        return self.filter(
            room=room, check_out_datetime__gt=check_in_datetime, check_in_datetime__lt=check_out_datetime
        ).count()

    def get_by_booking_id(self, booking_id: int):
        try:
            return self.get(id=booking_id)
        except ObjectDoesNotExist:
            return None
