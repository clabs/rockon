from __future__ import annotations

from uuid import uuid4

from django.db import models

from .attendance import Attendance
from .exhibitor import Exhibitor


class ExhibitorAttendance(models.Model):
    """ExhibitorAttendance model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    exhibitor = models.OneToOneField(
        Exhibitor, on_delete=models.CASCADE, related_name="attendance_count"
    )
    day = models.OneToOneField(
        Attendance, on_delete=models.CASCADE, related_name="exhibitors"
    )
    users_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.asset.name

    class Meta:
        ordering = ["exhibitor"]
