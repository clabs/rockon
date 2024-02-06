from __future__ import annotations

from rockon.base.models import Event
from rockon.base.models.organisation import Organisation
from rockon.library.custom_model import CustomModel, models


class ExhibitorStatus(models.TextChoices):
    UNKNOWN = "unknown", "Unbekannt"
    CONTACTED = "contacted", "Kontakt aufgenommen"
    CONFIRMED = "confirmed", "Bestätigt"
    REJECTED = "rejected", "Abgelehnt"


class Exhibitor(CustomModel):
    """Exhibitor model."""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="exhibitors"
    )
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="exhibitor"
    )
    state = models.CharField(
        max_length=12, choices=ExhibitorStatus.choices, default=ExhibitorStatus.UNKNOWN
    )
    market_id = models.CharField(
        max_length=255, default=None, null=True, blank=True, unique=True
    )
    general_note = models.TextField(null=True, default=None, blank=True)
    about_note = models.TextField(null=True, default=None, blank=True)
    offer_note = models.TextField(null=True, default=None, blank=True)
    internal_comment = models.TextField(null=True, default=None, blank=True)

    def __str__(self):
        return self.organisation.org_name
