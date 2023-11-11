from __future__ import annotations

from django.contrib.auth.models import User

from rockon.base.models import Event
from rockon.library.custom_model import CustomModel, models
from rockon.library.federal_states import FederalState
from rockon.library.guid import guid


class BidStatus(models.TextChoices):
    """Bid status."""

    UNKNOWN = "unknown", "Unbekannt"
    PENDING = "pending", "Bearbeitung"
    ACCEPTED = "accepted", "Angenommen"
    DECLINED = "declined", "Abgelehnt"


class Band(CustomModel):
    """Band model."""

    guid = models.CharField(max_length=255, default=guid, unique=True)
    slug = models.SlugField(default=None, blank=True, null=True, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bands")
    name = models.CharField(max_length=255)
    has_management = models.BooleanField(default=False)
    are_students = models.BooleanField(default=False)
    genre = models.CharField(max_length=32, default=None, blank=True, null=True)
    federal_state = models.CharField(
        max_length=255,
        default=None,
        blank=True,
        null=True,
        choices=FederalState.choices,
    )
    homepage = models.URLField(default=None, blank=True, null=True)
    facebook = models.URLField(default=None, blank=True, null=True)
    cover_letter = models.TextField(default=None, blank=True, null=True)
    contact = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="band",
        null=True,
        default=None,
        blank=True,
    )
    bid_status = models.CharField(
        max_length=32, default=BidStatus.UNKNOWN, choices=BidStatus.choices
    )
    techrider = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name
