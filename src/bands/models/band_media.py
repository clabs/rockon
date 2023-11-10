from __future__ import annotations

from library.custom_model import CustomModel, models

from .band import Band


def band_media_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"bids/{instance.band.id}/{filename}"


class MediaType(models.TextChoices):
    """Media type."""

    UNKNOWN = "unknown", "Unbekannt"
    DOCUMENT = "document", "Dokument"
    AUDIO = "audio", "Audio"
    LINK = "link", "Link"
    PRESS_PHOTO = "press_photo", "Pressefoto"
    LOGO = "logo", "Logo"


class BandMedia(CustomModel):
    """Band media model."""

    band = models.ForeignKey(Band, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(
        max_length=32, default=MediaType.UNKNOWN, choices=MediaType.choices
    )
    url = models.URLField(default=None, blank=True, null=True)
    file = models.FileField(
        upload_to=band_media_path, default=None, blank=True, null=True
    )
    thumbnail = models.ImageField(default=None, blank=True, null=True)
    file_name_original = models.CharField(
        max_length=512, default=None, blank=True, null=True
    )

    class Meta:
        ordering = ["band", "media_type", "created_at"]

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name_original = self.file.name
        super().save(*args, **kwargs)
