from __future__ import annotations

from rockon.library.custom_model import CustomModel, models


class Sponsoring(CustomModel):
    """Sponsoring model."""

    name = models.CharField(max_length=255)
    comment = models.CharField(max_length=511)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
