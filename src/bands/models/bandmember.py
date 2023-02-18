from __future__ import annotations

from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models

from event.models import Event

from .band import Band


class BandMember(models.Model):
    """Band member model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    band = models.OneToOneField(
        Band, on_delete=models.CASCADE, related_name="band_members"
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name
