from __future__ import annotations

from django.contrib.auth.models import User
from django.db.models import Q

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
    name = models.CharField(max_length=255, default=None, blank=True, null=True)
    has_management = models.BooleanField(default=False)
    are_students = models.BooleanField(default=False)
    genre = models.CharField(max_length=128, default=None, blank=True, null=True)
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
    repeated = models.BooleanField(default=False)
    techrider = models.JSONField(default=dict, blank=True, null=True)
    track = models.ForeignKey(
        "Track", on_delete=models.SET_NULL, null=True, related_name="bands"
    )
    bid_complete = models.BooleanField(default=False)

    def __str__(self):
        if self.name:
            return self.name
        return self.guid

    def save(self, *args, **kwargs):
        self.bid_complete = self.check_bid_complete()
        super().save(*args, **kwargs)

    def check_bid_complete(self) -> bool:
        fields = [
            self.name,
            self.genre,
            self.federal_state,
            self.homepage,
            self.facebook,
            self.cover_letter,
        ]

        audio_count = self.media.filter(media_type="audio").count() >= 3
        logo = self.media.filter(media_type="logo").count() >= 1
        press = self.media.filter(media_type="press_photo").count() >= 1

        conditions = [*fields, audio_count, logo, press]

        if all(conditions):
            return True

        return False

    def get_logo(self):
        return self.media.filter(media_type="logo").first()

    def get_press_photo(self):
        return self.media.filter(media_type="press_photo").first()

    def get_songs(self):
        query = self.media.filter(media_type="audio")
        if not query.exists():
            return None
        return query

    def get_links(self):
        return self.media.filter(media_type="link")

    def get_documents(self):
        return self.media.filter(media_type="document")
