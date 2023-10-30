from __future__ import annotations

from datetime import datetime

import pytz
from django.db import models

from .custom_model import CustomModel


class Event(CustomModel):
    name = models.CharField(max_length=255)
    opening_date = models.DateTimeField()
    closing_date = models.DateTimeField()
    tracks = models.ManyToManyField("Track", related_name="events", blank=True)

    def __str__(self):
        return self.name

    # Because we can not overwrite auto_now_add in Django
    # https://code.djangoproject.com/ticket/16583
    def save(self, auto_now: bool = True, *args, **kwargs):
        if self.created is None:
            self.created = datetime.now(pytz.utc)
        if auto_now:
            self.modified = datetime.now(pytz.utc)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["opening_date"]
