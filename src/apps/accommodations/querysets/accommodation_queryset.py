from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import models
from django.db.models import Q


class AccommodationQuerySet(models.QuerySet):
    def filter_by_location_and_status(self, city):
        """1. 지역과 활성 상태로 숙소 필터링"""
        return self.filter(Q(gps_info__city__in=city) & Q(is_active=True))

    def filter_by_available_rooms(self, available_rooms):
        """예약 가능한 방이 있는 숙소만 필터링"""
        return self.filter(Q(room__in=available_rooms)).distinct()

    def filter_by_radius(self, location: Point, radius: float):
        """지정된 위치와 반경 내의 숙소 필터링"""
        return self.filter(gps_info__location__distance_lte=(location, D(m=radius)))
