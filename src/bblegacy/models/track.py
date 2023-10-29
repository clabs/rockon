from __future__ import annotations

from django.db import models

from bblegacy.helper import guid

from .event import Event


class Track(models.Model):
    id = models.CharField(primary_key=True, max_length=255, default=guid)
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    visible = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
