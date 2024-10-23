# type: ignore

from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.db import models

from apps.users.models import BusinessUser


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
    image = models.ImageField(upload_to="accommodation_images")
    is_representative = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["accommodation", "is_representative"],
                condition=models.Q(is_representative=True),
                name="unique_representative_image_per_accommodation",
            )
        ]


class GPS_Info(gis_models.Model):
    accommodation = models.OneToOneField(Accommodation, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    states = models.CharField(max_length=100)
    road_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    location = gis_models.PointField(geography=True, srid=4326, default=Point(0.0, 0.0))  # 기본값 설정


class RefundPolicy(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="refund_policies")
    seven_days_before = models.DecimalField(max_digits=5, decimal_places=2)
    five_days_before = models.DecimalField(max_digits=5, decimal_places=2)
    three_days_before = models.DecimalField(max_digits=5, decimal_places=2)
    one_day_before = models.DecimalField(max_digits=5, decimal_places=2)
    same_day = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Refund Policy for {self.accommodation.name}"
