# type: ignore

from django.db import models

from apps.users.models import BusinessUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point


class Accommodation(models.Model):
    host = models.ForeignKey(BusinessUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    description = models.TextField()
    rules = models.TextField()
    average_rating = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AccommodationType(models.Model):
    accommodation = models.OneToOneField(Accommodation, on_delete=models.CASCADE)
    is_customized = models.BooleanField(default=False)
    type_name = models.CharField(max_length=100)


class Accommodation_Image(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="accommodation_images/")


class GPS_Info(gis_models.Model):
    accommodation = models.OneToOneField(Accommodation, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    states = models.CharField(max_length=100)
    road_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    location = gis_models.PointField(geography=True, srid=4326, default=Point(0.0, 0.0))  # 기본값 설정
