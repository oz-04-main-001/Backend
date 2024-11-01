from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate


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

    def filter_daily_bookings(self, host_profile, month, year, status_list):
        return  self.filter(
                room__accommodation__host=host_profile,
                check_in_datetime__year=year,
                check_in_datetime__month=month,
                status__in=status_list,
            )