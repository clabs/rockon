from __future__ import annotations

from rockon.base.models import Event
from rockon.library.custom_model import CustomModel, models


class Track(CustomModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(default=None, blank=True, null=True, unique=True)
    events = models.ManyToManyField(
        Event, default=None, blank=True, related_name="tracks"
    )
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Track"
        verbose_name_plural = "Tracks"
        ordering = ("name",)

    def __str__(self):
        return self.name
