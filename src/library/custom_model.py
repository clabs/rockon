from __future__ import annotations

from uuid import uuid4

from django.db import models


class CustomModel(models.Model):
    """Custom model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["created_at"]


# from library.custom_model import CustomModel, models
