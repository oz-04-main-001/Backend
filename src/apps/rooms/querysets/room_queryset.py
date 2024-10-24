from datetime import datetime

from django.db import models
from django.db.models import Q


class RoomQuerySet(models.QuerySet):
    def get_by_room_id(self, room_id):
        return self.get(id=room_id)

    def available(self):
        return self.filter(is_available=True)

    def by_accommodation(self, accommodation_id):
        return self.filter(accommodation_id=accommodation_id)

    def within_capacity_range(self, guests_count):
        return self.filter(capacity__lte=guests_count, max_capacity__gte=guests_count)

    def in_price_range(self, min_price, max_price):
        return self.filter(price__gte=min_price, price__lte=max_price)

    def available_for_dates(self, check_in_date, check_out_date):
        return self.exclude(Q(booking__check_in_date__lt=check_out_date) & Q(booking__check_out_date__gt=check_in_date))

    def with_amenities(self, amenity_ids):
        return self.filter(amenities__id__in=amenity_ids).distinct()
