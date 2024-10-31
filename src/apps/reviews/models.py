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


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # 댓글 수정 시간
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    is_active = models.BooleanField(default=True)  # 댓글 활성화 여부
    comment_level = models.PositiveIntegerField(default=0)  # 댓글 깊이

    class Meta:
        ordering = ["created_at"]