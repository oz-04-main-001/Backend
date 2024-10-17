# apps/rooms/models.py

from apps.accommodations.models import Accommodation
from django.db import models


class Room(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    capacity = models.IntegerField()
    max_capacity = models.IntegerField()
    price = models.IntegerField()
    stay_type = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    is_available = models.BooleanField(default=True)


class RoomType(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    is_customized = models.BooleanField(default=False)
    type_name = models.CharField(max_length=100)


class Room_Image(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="room_images/")


class RoomInventory(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    count_room = models.IntegerField()
