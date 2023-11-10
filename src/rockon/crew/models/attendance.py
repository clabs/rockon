from __future__ import annotations

from rockon.event.models import Event
from rockon.library.custom_model import CustomModel, models


class AttendancePhase(models.TextChoices):
    SETUP = "setup", "Aufbau"
    SHOW = "show", "Veranstaltung"
    TEARDOWN = "teardown", "Abbau"


class Attendance(CustomModel):
    """Attendance model."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    day = models.DateField()
    phase = models.CharField(max_length=10, choices=AttendancePhase.choices)

    def __str__(self):
        return self.day.strftime("%d.%m.%Y")

    @classmethod
    def get_phases(cls, event: Event) -> tuple[list[tuple[str, str]], list[Attendance]]:
        days = cls.objects.filter(event=event)
        list_of_phases = []
        for phase in AttendancePhase.choices:
            _phase = {
                "phase": phase[0],
                "name": phase[1],
                "days": days.filter(phase=phase[0]),
            }
            list_of_phases.append(_phase)
        return list_of_phases

    class Meta:
        ordering = ["day"]
