from __future__ import annotations

import json
import logging

from django.core.serializers import serialize
from django_q.tasks import AsyncTask

from rockon.library.custom_model import CustomModel, models

from .band import Band

logger = logging.getLogger(__name__)


def band_media_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'bids/{instance.band.id}/{filename}'


class MediaType(models.TextChoices):
    """Media type."""

    UNKNOWN = 'unknown', 'Unbekannt'
    AUDIO = 'audio', 'Audio'
    DOCUMENT = 'document', 'Dokument'
    LINK = 'link', 'Link'
    LOGO = 'logo', 'Logo'
    PRESS_PHOTO = 'press_photo', 'Pressefoto'
    WEB = 'web', 'Webseite'


class EncodeStatus(models.TextChoices):
    """Encode status."""

    PENDING = 'pending', 'Ausstehend'
    DONE = 'done', 'Fertig'
    FAILED = 'failed', 'Fehlgeschlagen'


class BandMedia(CustomModel):
    """Band media model."""

    band = models.ForeignKey(Band, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(
        max_length=32, default=MediaType.UNKNOWN, choices=MediaType.choices
    )
    url = models.URLField(default=None, blank=True, null=True)
    file = models.FileField(
        upload_to=band_media_path, default=None, blank=True, null=True, max_length=500
    )
    encoded_file = models.FileField(
        upload_to=band_media_path, default=None, blank=True, null=True
    )
    thumbnail = models.ImageField(default=None, blank=True, null=True)
    file_name_original = models.CharField(
        max_length=512, default=None, blank=True, null=True
    )
    encode_status = models.CharField(
        max_length=16,
        default=EncodeStatus.PENDING,
        db_default=EncodeStatus.PENDING,
        choices=EncodeStatus.choices,
    )
    encode_error = models.CharField(max_length=255, default=None, blank=True, null=True)

    class Meta:
        ordering = ('band', 'media_type', 'created_at')

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.file and not self.file_name_original:
            self.file_name_original = self.file.name
        super().save(*args, **kwargs)

    def encode_file(self):
        """Encode file.

        Dispatches encoding to a django-q worker.  If the broker is
        unreachable the error is logged and swallowed so the calling
        view can still return a timely HTTP response.
        """
        if not self.file:
            return
        try:
            if self.media_type == MediaType.AUDIO:
                _task = AsyncTask(
                    'rockon.bands.services.media_encoding.encode_audio_file',
                    self.id,
                    group='encode_audio_file',
                )
                _task.run()
            elif self.media_type in (MediaType.PRESS_PHOTO, MediaType.LOGO):
                _task = AsyncTask(
                    'rockon.bands.services.media_encoding.encode_image_file',
                    self.id,
                    group='encode_image_file',
                )
                _task.run()
        except Exception:
            logger.exception(
                'Failed to enqueue encode task for BandMedia %s. '
                'The broker may be unavailable.',
                self.id,
            )
        return

    def json_dump(self):
        """JSON dump."""
        instance_json_str = serialize('json', [self])
        instance_json = json.loads(instance_json_str)[0]
        _instance = {}
        _instance['id'] = instance_json['pk']
        _instance.update(instance_json['fields'])

        return _instance
