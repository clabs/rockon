from __future__ import annotations

from uuid import uuid4

from django.db import models


class Timeline(models.Model):
    """Timeline model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    comment = models.CharField(max_length=511)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
