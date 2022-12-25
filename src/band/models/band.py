from __future__ import annotations

from uuid import uuid4

from django.db import models

from crm.models import Person
from event.models import Event


class Band(models.Model):
    """Band model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    contact = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
