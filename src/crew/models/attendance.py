from __future__ import annotations

from uuid import uuid4

from django.db import models

from event.models import Event


class Attendance(models.Model):
    """Attendance model."""

    PHASE = [
        ("setup", "Aufbau"),
        ("show", "Veranstaltung"),
        ("teardown", "Abbau"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    day = models.DateField()
    phase = models.CharField(max_length=10, choices=PHASE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.day.strftime("%A, %d.%m.%Y")

    @classmethod
    def get_phases(cls, event: Event) -> tuple[list[tuple[str, str]], list[Attendance]]:
        days = cls.objects.filter(event=event)
        list_of_phases = []
        for phase in cls.PHASE:
            _phase = {
                "phase": phase[0],
                "name": phase[1],
                "days": days.filter(phase=phase[0]),
            }
            list_of_phases.append(_phase)
        return list_of_phases

    class Meta:
        ordering = ["day"]
