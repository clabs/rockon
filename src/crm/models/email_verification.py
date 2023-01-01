from __future__ import annotations

from uuid import uuid4

from django.db import models

from .person import Person


class EmailVerification(models.Model):
    """EmailVerification model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="email_verifications"
    )
    token = models.UUIDField(default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["person"]
