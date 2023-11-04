from __future__ import annotations

from library.custom_model import CustomModel, models

from .asset import Asset


class ExhibitorAsset(CustomModel):
    """ExhibitorAsset model."""

    exhibitor = models.ForeignKey(
        "Exhibitor", on_delete=models.CASCADE, related_name="assets"
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="exhibitor")
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.asset.name

    class Meta:
        ordering = ["asset"]
