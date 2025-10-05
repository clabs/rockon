from __future__ import annotations

from rockon.library.custom_model import CustomModel, models


class AttendanceAddition(CustomModel):
    """Attendance additions model."""

    attendance = models.ForeignKey('Attendance', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.attendance.day.strftime("%A, %d.%m.%Y")}+{self.amount}'
