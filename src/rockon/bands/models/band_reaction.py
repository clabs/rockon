from __future__ import annotations

from django.contrib.auth.models import User

from rockon.library.custom_model import CustomModel, models

from .band import Band

ALLOWED_EMOJIS = ['🔥', '🎸', '🤘', '❤️', '👏', '👎']


class BandReaction(CustomModel):
    """Live emoji reaction on a band."""

    band = models.ForeignKey(Band, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='band_reactions'
    )
    emoji = models.CharField(max_length=8)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.emoji} by {self.user} on {self.band}'
