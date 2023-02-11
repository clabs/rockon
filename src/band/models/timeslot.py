from __future__ import annotations

from uuid import uuid4

from django.db import models

from .band import Band
from .stage import Stage


class TimeSlot(models.Model):
    """TimeSlot model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    stage = models.OneToOneField(Stage, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    band = models.OneToOneField(
        Band, on_delete=models.CASCADE, null=True, blank=True, related_name="time_slot"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.start} - {self.end}"
