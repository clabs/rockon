from __future__ import annotations

from os import path
from uuid import uuid4

from django.db import models
from django.utils.deconstruct import deconstructible

from crm.models import Person


@deconstructible
class UploadToPathAndRename:
    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split(".")[-1]
        filename = f"{instance.uuid}.{ext}"
        return path.join(self.sub_path, filename)


class Team(models.Model):
    """Team model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    lead = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=True, blank=True, related_name="lead"
    )
    vize_lead = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="vize_lead",
    )
    image = models.ImageField(
        upload_to=UploadToPathAndRename(path.join("teams")),
        blank=True,
        null=True,
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
