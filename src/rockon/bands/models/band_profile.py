from __future__ import annotations

from django.contrib.auth.models import User

from rockon.library.custom_model import CustomModel, models
from rockon.library.guid import guid


class BandProfile(CustomModel):
    """Band identity that persists across events; each yearly bid is a `Band` row."""

    guid = models.CharField(max_length=255, default=guid, unique=True)
    name = models.CharField(max_length=255, default=None, blank=True, null=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='band_profiles',
        null=True,
        default=None,
        blank=True,
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        if self.name:
            return self.name
        return self.guid

    def latest_bid(self):
        return self.bids.order_by('-event__start').first()
