from __future__ import annotations

from django.contrib.auth.models import User

from rockon.library.custom_model import CustomModel, models

from .band import Band


class Comment(CustomModel):
    """Comment model."""

    band = models.ForeignKey(Band, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    reason = models.TextField(default=None, blank=True, null=True)
    mood = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.created_at}"
