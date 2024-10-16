# apps/bookmarks/models.py

from django.db import models
from apps.users.models import User
from apps.accommodations.models import Accommodation


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "accommodation")
