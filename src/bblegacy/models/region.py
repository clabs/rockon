from __future__ import annotations

from django.db import models

from .custom_model import CustomModel


class Region(CustomModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Region"
        verbose_name_plural = "Regionen"
