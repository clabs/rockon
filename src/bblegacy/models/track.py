from __future__ import annotations

from django.db import models

from .custom_model import CustomModel
from .event import Event


class Track(CustomModel):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    visible = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
