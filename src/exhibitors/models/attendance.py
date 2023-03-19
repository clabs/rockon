from __future__ import annotations

from uuid import uuid4

from django.db import models

from event.models import Event


class Attendance(models.Model):
    """Attendance model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="exhibitor_attendances"
    )
    day = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["day"]
