from __future__ import annotations

from uuid import uuid4

from django.db import models
from django.templatetags.static import static

from library import UploadToPathAndRename


class TeamCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=1024)
    description = models.TextField()
    image = models.ImageField(
        upload_to=UploadToPathAndRename("teams"),
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Team categories"

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static("assets/4_3_placeholder.png")
