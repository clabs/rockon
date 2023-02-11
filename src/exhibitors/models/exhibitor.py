from __future__ import annotations

from uuid import uuid4

from django.db import models

from crm.models.organisation import Organisation
from event.models import Event

from .attendance import Attendance


class Exhibitor(models.Model):
    """Exhibitor model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    organization = models.OneToOneField(
        Organisation, on_delete=models.CASCADE, related_name="exhibitor"
    )
    name = models.CharField(max_length=255)
    attendance = models.ManyToManyField(Attendance, blank=True)
    is_confirmed = models.BooleanField(default=False)
    market_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
