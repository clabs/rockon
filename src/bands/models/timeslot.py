from __future__ import annotations

from uuid import uuid4

from django.db import models

from crew.models import Attendance

from .stage import Stage


class TimeSlot(models.Model):
    """TimeSlot model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="timeslots")
    day = models.ForeignKey(
        Attendance, on_delete=models.CASCADE, related_name="timeslots"
    )
    start = models.TimeField()
    end = models.TimeField()
    band = models.OneToOneField(
        "Band",
        on_delete=models.CASCADE,
        related_name="slot",
        null=True,
        default=None,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.day} - {self.start} - {self.end}"
