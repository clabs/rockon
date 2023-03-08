from __future__ import annotations

from os import path
from uuid import uuid4

from django.db import models
from django.templatetags.static import static

from library import UploadToPathAndRename


class Event(models.Model):
    """Event model."""

    SIGN_UP_TYPE = [
        ("unknown", "Unbekannt"),
        ("crew", "Crew"),
        ("exhibitor", "Austeller"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
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
    location = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    image = models.ImageField(
        upload_to=UploadToPathAndRename(path.join("events")),
        blank=True,
        null=True,
    )
    sub_event_of = models.OneToOneField(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="sub_events",
    )
    show_on_landing_page = models.BooleanField(default=False)
    signup_is_open = models.BooleanField(default=True)
    signup_type = models.CharField(
        max_length=12, choices=SIGN_UP_TYPE, default="unknown"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["start"]

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static("assets/4_3_placeholder.png")
