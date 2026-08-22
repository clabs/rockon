from __future__ import annotations

from rockon.library.custom_model import CustomModel, models

from .attendance import Attendance


class ExhibitorAttendance(CustomModel):
    """ExhibitorAttendance model."""

    exhibitor = models.ForeignKey(
        'Exhibitor', on_delete=models.CASCADE, related_name='attendances'
    )
    day = models.ForeignKey(
        Attendance, on_delete=models.CASCADE, related_name='exhibitors'
    )
    count = models.IntegerField(default=0)
