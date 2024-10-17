# apps/bookmarks/models.py

from apps.accommodations.models import Accommodation
from apps.users.models import User
from django.db import models


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "accommodation")
