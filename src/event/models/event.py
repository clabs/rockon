from __future__ import annotations

from os import path
from uuid import uuid4

from django.db import models
from django.utils.deconstruct import deconstructible


@deconstructible
class UploadToPathAndRename:
    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split(".")[-1]
        filename = f"{instance.uuid}.{ext}"
        return path.join(self.sub_path, filename)


class Event(models.Model):
    """Event model."""

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
    image = models.ImageField(
        upload_to=UploadToPathAndRename(path.join("events")),
        blank=True,
        null=True,
    )
    sub_event_of = models.OneToOneField(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["start"]
