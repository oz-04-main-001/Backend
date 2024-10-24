# type: ignore

from django.db import models

from apps.bookings.querysets.booking_queryset import BookingQuerySet
from apps.common.choices import BOOKING_STATUS_CHOICES
from apps.rooms.models import Room
from apps.users.models import User


class Booking(models.Model):
    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_datetime = models.DateTimeField()
    check_out_datetime = models.DateTimeField()
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=30, choices=BOOKING_STATUS_CHOICES, default="pending")
    request = models.TextField(null=True, blank=True)
    guests_count = models.PositiveIntegerField(default=1)
    booker_name = models.CharField(max_length=100)
    booker_phone_number = models.CharField(max_length=20)

    objects = BookingQuerySet.as_manager()
