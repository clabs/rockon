from __future__ import annotations

from django.contrib.auth.models import User

from event.models import Event
from library.custom_model import CustomModel, models


class Band(CustomModel):
    """Band model."""

    slug = models.SlugField(default=None, blank=True, null=True, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bands")
    name = models.CharField(max_length=255)
    contact = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="band",
        null=True,
        default=None,
        blank=True,
    )
    techrider = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name
