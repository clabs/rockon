from __future__ import annotations

from uuid import uuid4

from django.db import models


class Shirt(models.Model):
    """Shirt model."""

    CUT = [
        ("straight", "Regulär"),
        ("fitted", "Figurbetont"),
    ]

    SIZE = [
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("2XL", "2XL"),
        ("3XL", "3XL"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    size = models.CharField(max_length=12, choices=SIZE)
    cut = models.CharField(max_length=12, choices=CUT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cut} - {self.size}"

    class Meta:
        ordering = ["cut", "size"]
