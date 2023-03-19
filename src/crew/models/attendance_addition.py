from __future__ import annotations

from uuid import uuid4

from django.db import models


class AttendanceAddition(models.Model):
    """Attendance additions model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    attendance = models.ForeignKey("Attendance", on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.attendance.day.strftime("%A, %d.%m.%Y")}+{self.amount}'
