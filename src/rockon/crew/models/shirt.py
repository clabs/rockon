from __future__ import annotations

from rockon.library.custom_model import CustomModel, models


class ShirtCut(models.TextChoices):
    STRAIGHT = "straight", "Regulär"
    FITTED = "fitted", "Figurbetont"


class ShirtSize(models.TextChoices):
    S = "S", "S"
    M = "M", "M"
    L = "L", "L"
    XL = "XL", "XL"
    XXL = "2XL", "2XL"
    XXXL = "3XL", "3XL"
    XXXXL = "4XL", "4XL"


class Shirt(CustomModel):
    """Shirt model."""

    size = models.CharField(max_length=12, choices=ShirtSize.choices)
    cut = models.CharField(max_length=12, choices=ShirtCut.choices)

    def __str__(self):
        return f"{self.cut} - {self.size}"

    class Meta:
        ordering = ["cut", "size"]
