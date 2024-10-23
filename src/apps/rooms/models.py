# type: ignore

from django.db import models

from apps.accommodations.models import Accommodation
from apps.rooms.querysets.room_queryset import RoomQuerySet


class Room(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    capacity = models.IntegerField()
    max_capacity = models.IntegerField()
    price = models.IntegerField()
    stay_type = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    objects = RoomQuerySet.as_manager()


class RoomType(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    is_customized = models.BooleanField(default=False)
    type_name = models.CharField(max_length=100)


class Room_Image(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="room_images")
    is_representative = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["room", "is_representative"],
                condition=models.Q(is_representative=True),
                name="unique_representative_image_per_room",
            )
        ]


class RoomInventory(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    count_room = models.IntegerField()
