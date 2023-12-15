from __future__ import annotations

import os
import subprocess

from django.conf import settings
from django_q.tasks import AsyncTask

from rockon.library.custom_model import CustomModel, models

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
    encoded_file = models.FileField(
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
        if self.file and not self.file_name_original:
            self.file_name_original = self.file.name
        super().save(*args, **kwargs)

    def encode_file(self):
        """Encode file."""
        if not self.file:
            return
        if self.media_type == MediaType.AUDIO:
            _task = AsyncTask(
                "rockon.bands.models.band_media.BandMedia.encode_audio_file",
                self.id,
                group="encode_audio_file",
            )
            _task.run()
        elif (
            self.media_type == MediaType.PRESS_PHOTO
            or self.media_type == MediaType.LOGO
        ):
            _task = AsyncTask(
                "rockon.bands.models.band_media.BandMedia.encode_image_file",
                self.id,
                group="encode_image_file",
            )
            _task.run()
        return

    @classmethod
    def encode_audio_file(cls, id) -> BandMedia:
        """Encode audio file."""
        _file = cls.objects.get(id=id)
        if not _file.file:
            return
        file_name = os.path.basename(_file.file.name)
        file_name_without_extension = "".join(file_name.split(".")[:-1])

        new_file_name = f"{file_name_without_extension}-encoded.mp3"
        new_absolute_path = os.path.abspath(
            os.path.join(os.path.dirname(_file.file.path), new_file_name)
        )

        new_relative_path = os.path.join(
            os.path.dirname(
                os.path.relpath(_file.file.path, start=settings.MEDIA_ROOT)
            ),
            new_file_name,
        )

        ffmpeg_bin = settings.FFMPEG_BIN
        ffmpeg_cmd = f"{ffmpeg_bin} -y -hide_banner -i {_file.file.path} -vn -c:a libmp3lame -b:a 128k -ar 44100 {new_absolute_path}"
        return_code = subprocess.call(ffmpeg_cmd, shell=True)

        if return_code != 0:
            raise RuntimeError("Encoding failed")

        _file.encoded_file = new_relative_path
        _file.save()

        return _file

    @classmethod
    def encode_image_file(cls, id) -> BandMedia:
        """ "Encode image file."""
        _file = cls.objects.get(id=id)
        if not _file.file:
            return
        file_name = os.path.basename(_file.file.name)
        file_name_without_extension = "".join(file_name.split(".")[:-1])

        new_file_name = f"{file_name_without_extension}-thumbnail.png"
        new_absolute_path = os.path.abspath(
            os.path.join(os.path.dirname(_file.file.path), new_file_name)
        )

        new_relative_path = os.path.join(
            os.path.dirname(
                os.path.relpath(_file.file.path, start=settings.MEDIA_ROOT)
            ),
            new_file_name,
        )

        convert_bin = settings.CONVERT_BIN
        convert_cmd = (
            f"{convert_bin} {_file.file.path} -resize 400x {new_absolute_path}"
        )
        return_code = subprocess.call(convert_cmd, shell=True)

        if return_code != 0:
            raise RuntimeError("Encoding failed")

        _file.encoded_file = new_relative_path
        _file.save()

        return _file
