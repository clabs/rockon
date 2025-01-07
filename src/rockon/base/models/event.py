from __future__ import annotations

from os import path

from django.templatetags.static import static
from slugify import slugify

from rockon.library import UploadToPathAndRename
from rockon.library.custom_model import CustomModel, models


class SignUpType(models.TextChoices):
    UNKNOWN = "unknown", "Unbekannt"
    CREW = "crew", "Crew"
    EXHIBITOR = "exhibitor", "Aussteller"


class Event(CustomModel):
    """Event model."""

    name = models.CharField(max_length=511)
    slug = models.SlugField(null=False, unique=True)
    description = models.TextField()
    start = models.DateField(help_text="Veranstaltung beginnt")
    end = models.DateField(help_text="Veranstaltung endet")
    setup_start = models.DateField(help_text="Aufbau beginnt")
    setup_end = models.DateField(help_text="Aufbau endet")
    opening = models.DateField(help_text="Erster Einlass")
    closing = models.DateField(help_text="Ende der Veranstaltung")
    teardown_start = models.DateField(help_text="Abbau beginnt")
    teardown_end = models.DateField(help_text="Abbau endet")
    band_application_start = models.DateTimeField(
        blank=True, null=True, help_text="Bandbewerbung beginnt"
    )
    band_application_end = models.DateTimeField(
        blank=True, null=True, help_text="Bandbewerbung endet"
    )
    exhibitor_application_start = models.DateTimeField(
        blank=True, null=True, help_text="Ausstellerbewerbung beginnt"
    )
    exhibitor_application_end = models.DateTimeField(
        blank=True, null=True, help_text="Ausstellerbewerbung endet"
    )
    location = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    image = models.ImageField(
        upload_to=UploadToPathAndRename(path.join("events")),
        blank=True,
        null=True,
    )
    sub_event_of = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="sub_events",
    )
    show_on_landing_page = models.BooleanField(default=False)
    signup_is_open = models.BooleanField(
        default=True,
        help_text="Crew Anmeldung und Bandbewerbung werden auf der Website angezeigt",
    )
    signup_type = models.CharField(
        max_length=12, choices=SignUpType.choices, default=SignUpType.UNKNOWN
    )
    is_current = models.BooleanField(default=False)
    bid_vote_allowed = models.BooleanField(
        default=False, help_text="Bandbewertung aktiv"
    )
    bid_browsing_allowed = models.BooleanField(
        default=False, help_text="Bandbewerbungen einsehbar"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["start"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.slug == "":
            self.slug = str(self.id)
        super().save(*args, **kwargs)

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static("assets/4_3_placeholder.webp")

    @property
    def band_application_open(self) -> bool:
        from django.utils import timezone

        if not self.band_application_start or not self.band_application_end:
            return False

        return (
            self.band_application_start <= timezone.now() <= self.band_application_end
        )

    @property
    def exhibitor_application_open(self) -> bool:
        from django.utils import timezone

        if not self.exhibitor_application_start or not self.exhibitor_application_end:
            return False

        return (
            self.exhibitor_application_start
            <= timezone.now()
            <= self.exhibitor_application_end
        )

    @classmethod
    def get_current_event(cls) -> Event:
        return cls.objects.filter(is_current=True).order_by("-start").first()
