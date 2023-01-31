from __future__ import annotations

from uuid import uuid4

from django.db import models


class Asset(models.Model):
    """Asset model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    explanation = models.TextField(blank=True)
    is_bool = models.BooleanField(default=False)
    icon = models.CharField(
        max_length=255,
        help_text='<a target="_blank" href="https://semantic-ui.com/elements/icon.html">Wähle ein Icon aus</a>',
        default="heart",
    )
    internal_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
