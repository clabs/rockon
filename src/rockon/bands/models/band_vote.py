from __future__ import annotations

from django.contrib.auth.models import User

from rockon.library.custom_model import CustomModel, models

from .band import Band


class BandVote(CustomModel):
    """Band vote model."""

    band = models.ForeignKey(Band, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="band_votes")
    vote = models.IntegerField()

    class Meta:
        ordering = ["band", "user", "created_at"]

    def __str__(self):
        return f"vote:{self.user}:{self.band}"
