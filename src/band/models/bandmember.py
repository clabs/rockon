from __future__ import annotations

from uuid import uuid4

from django.db import models

from crm.models import Person
from event.models import Event

from .band import Band


class BandMember(models.Model):
    """Band member model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    band = models.ForeignKey(
        Band, on_delete=models.CASCADE, related_name="band_members"
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.person.name
