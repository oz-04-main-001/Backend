# type: ignore

from django.db import models

from apps.accommodations.models import Accommodation
from apps.common.choices import RATING_CHOICES
from apps.users.models import User


class Review(models.Model):
    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Rating(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE)
    rating = models.CharField(max_length=1, choices=RATING_CHOICES)
