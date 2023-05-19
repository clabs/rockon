from __future__ import annotations

from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models

from event.models import Event


class Band(models.Model):
    """Band model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
