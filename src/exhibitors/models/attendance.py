from __future__ import annotations

from event.models import Event
from library.custom_model import CustomModel, models


class Attendance(CustomModel):
    """Attendance model."""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="exhibitor_attendances"
    )
    day = models.DateField()

    def __str__(self):
        return self.day.strftime("%d.%m.%Y")

    class Meta:
        ordering = ["day"]
