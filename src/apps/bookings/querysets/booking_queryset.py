from django.db import models
from django.db.models import Q


class BookingQuerySet(models.QuerySet):
    def overlapping(self, room, check_in_date, check_out_date):
        return self.filter(room=room, check_out_date__gt=check_in_date, check_in_date__lt=check_out_date)
