from __future__ import annotations

from rockon.base.models import Event
from rockon.library.custom_model import CustomModel, models


class Crew(CustomModel):
    """Crew model."""

    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="crews")
    name = models.CharField(max_length=255)
    year = models.IntegerField()

    def __str__(self):
        return self.name
