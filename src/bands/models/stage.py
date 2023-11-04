from __future__ import annotations

from event.models import Event
from library.custom_model import CustomModel, models


class Stage(CustomModel):
    """Stage model."""

    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
