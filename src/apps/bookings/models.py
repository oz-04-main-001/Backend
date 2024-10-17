# apps/bookings/models.py

from apps.common.choices import BOOKING_STATUS_CHOICES
from apps.rooms.models import Room
from apps.users.models import User
from django.db import models


class Booking(models.Model):
    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.IntegerField()
    status = models.CharField(
        max_length=20, choices=BOOKING_STATUS_CHOICES, default="pending"
    )
    request = models.TextField(null=True, blank=True)
