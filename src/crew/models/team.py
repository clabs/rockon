from __future__ import annotations

from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.templatetags.static import static

from library import UploadToPathAndRename

from .team_category import TeamCategory


class Team(models.Model):
    """Team model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    lead = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="lead"
    )
    vize_lead = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="vize_lead",
    )
    image = models.ImageField(
        upload_to=UploadToPathAndRename("teams"),
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        TeamCategory,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="teams",
    )
    contact_mail = models.EmailField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    show_teamlead = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static("assets/4_3_placeholder.png")
