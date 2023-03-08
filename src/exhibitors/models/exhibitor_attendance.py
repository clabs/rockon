from __future__ import annotations

from uuid import uuid4

from django.db import models

from .attendance import Attendance


class ExhibitorAttendance(models.Model):
    """ExhibitorAttendance model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    exhibitor = models.ForeignKey(
        "Exhibitor", on_delete=models.CASCADE, related_name="attendances"
    )
    day = models.ForeignKey(
        Attendance, on_delete=models.CASCADE, related_name="exhibitors"
    )
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
