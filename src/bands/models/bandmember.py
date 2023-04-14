from __future__ import annotations

from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models

from crew.models import CrewMemberNutrion

from .band import Band


class BandMemberPosition(models.TextChoices):
    UNKNOWN = "unknown", "Unbekannt"
    MERCH = "merch", "Merchandise"
    BAND = "band", "Band"
    HAND = "hand", "Stagehand"


class BandMember(models.Model):
    """Band member model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    band = models.ForeignKey(
        Band, on_delete=models.CASCADE, related_name="band_members"
    )
    nutrition = models.CharField(
        max_length=12,
        choices=CrewMemberNutrion.choices,
        default=CrewMemberNutrion.UNKNOWN,
    )
    position = models.CharField(
        max_length=12,
        choices=BandMemberPosition.choices,
        default=BandMemberPosition.UNKNOWN,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
