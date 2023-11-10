from __future__ import annotations

from rockon.crew.models import Attendance
from rockon.library.custom_model import CustomModel, models

from .stage import Stage


class TimeSlot(CustomModel):
    """TimeSlot model."""

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

    def __str__(self):
        return f"{self.day} - {self.start} - {self.end}"
