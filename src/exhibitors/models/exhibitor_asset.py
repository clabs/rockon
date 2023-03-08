from __future__ import annotations

from uuid import uuid4

from django.db import models

from .asset import Asset


class ExhibitorAsset(models.Model):
    """ExhibitorAsset model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    exhibitor = models.ForeignKey(
        "Exhibitor", on_delete=models.CASCADE, related_name="assets"
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="exhibitor")
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.asset.name

    class Meta:
        ordering = ["asset"]
