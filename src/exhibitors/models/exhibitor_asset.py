from __future__ import annotations

from uuid import uuid4

from django.db import models

from .asset import Asset
from .exhibitor import Exhibitor


class ExhibitorAsset(models.Model):
    """ExhibitorAsset model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    exhibitor = models.OneToOneField(
        Exhibitor, on_delete=models.CASCADE, related_name="asset"
    )
    asset = models.OneToOneField(
        Asset, on_delete=models.CASCADE, related_name="exhibitor"
    )
    is_checked = models.BooleanField(blank=True, null=True)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.asset.name

    class Meta:
        ordering = ["asset"]
