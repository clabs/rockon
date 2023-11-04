from __future__ import annotations

from django.contrib.auth.models import User

from crew.models import CrewMemberNutrion
from library.custom_model import CustomModel, models

from .band import Band


class BandMemberPosition(models.TextChoices):
    UNKNOWN = "unknown", "Unbekannt"
    MERCH = "merch", "Merchandise"
    BAND = "band", "Band"
    HAND = "hand", "Stagehand"
    TECHNICAN = "technican", "Techniker"
    SUPPORT = "support", "Support"


class BandMember(CustomModel):
    """Band member model."""

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

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
