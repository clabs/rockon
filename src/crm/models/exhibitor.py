from __future__ import annotations

from uuid import uuid4

from django.db import models

from event.models import Event

from .organisation import Organisation


class Exhibitor(models.Model):
    """Exhibitor model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="exhibitors"
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
