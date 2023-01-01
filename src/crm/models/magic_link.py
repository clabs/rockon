from __future__ import annotations

from uuid import uuid4

from django.db import models

from .person import Person


class MagicLink(models.Model):
    """MagicLink model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="magic_links"
    )
    token = models.UUIDField(default=uuid4, editable=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["person", "expires_at"]
