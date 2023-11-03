from __future__ import annotations

from uuid import uuid4

from django.db import models


class AccountContext(models.Model):
    """AccountContext model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    slug = models.SlugField(max_length=1024)
    name = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return self.name
        return self.slug

    class Meta:
        ordering = ["slug"]
