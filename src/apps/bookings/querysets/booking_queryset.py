from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class BookingQuerySet(models.QuerySet):
    def overlapping(self, room, check_in_date, check_out_date):
        return self.filter(room=room, check_out_date__gt=check_in_date, check_in_date__lt=check_out_date).count()

    def get_by_booking_id(self, booking_id: int):
        try:
            return self.get(id=booking_id)
        except ObjectDoesNotExist:
            return None
