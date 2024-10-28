from django.db import models
from django.db.models import Q


class AccommodationQuerySet(models.QuerySet):
    def filter_by_location_and_status(self, state):
        """1. 지역과 활성 상태로 숙소 필터링"""
        return self.filter(Q(gps_info__states=state) & Q(is_active=True))

    def filter_by_available_rooms(self, available_rooms):
        """예약 가능한 방이 있는 숙소만 필터링"""
        return self.filter(Q(room__in=available_rooms)).distinct()
