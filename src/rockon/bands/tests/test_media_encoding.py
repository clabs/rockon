from __future__ import annotations

import uuid
from datetime import date, timedelta
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from rockon.bands.models import Band, BandMedia, EncodeStatus, MediaType
from rockon.bands.services import media_encoding
from rockon.base.models import Event
from rockon.base.models.event import SignUpType


def _make_event() -> Event:
    start = date(2026, 7, 1)
    return Event.objects.create(
        name='Rocktreff 2026',
        slug=f'rocktreff-{uuid.uuid4().hex[:8]}',
        description='desc',
        start=start,
        end=start + timedelta(days=2),
        setup_start=start - timedelta(days=2),
        setup_end=start - timedelta(days=1),
        opening=start,
        closing=start + timedelta(days=1),
        teardown_start=start + timedelta(days=2),
        teardown_end=start + timedelta(days=3),
        location='Berlin',
        signup_type=SignUpType.CREW,
        signup_is_open=True,
    )


class MediaEncodingTests(TestCase):
    def setUp(self):
        self.band = Band.objects.create(event=_make_event(), name='Encode Band')

    def _make_audio_media(self) -> BandMedia:
        return BandMedia.objects.create(
            band=self.band,
            media_type=MediaType.AUDIO,
            file=SimpleUploadedFile(
                'song.mp3', b'\x00' * 32, content_type='audio/mpeg'
            ),
        )

    def _make_image_media(self) -> BandMedia:
        return BandMedia.objects.create(
            band=self.band,
            media_type=MediaType.LOGO,
            file=SimpleUploadedFile('logo.png', b'\x89PNG\r\n\x1a\n' + b'\x00' * 32),
        )

    @patch('rockon.bands.services.media_encoding.subprocess.call', return_value=0)
    def test_encode_audio_file_marks_done_on_success(self, _mock_call):
        media = self._make_audio_media()

        result = media_encoding.encode_audio_file(media.id)

        self.assertEqual(result.encode_status, EncodeStatus.DONE)
        self.assertTrue(result.encoded_file)
        self.assertIsNone(result.encode_error)

    @patch('rockon.bands.services.media_encoding.subprocess.call', return_value=1)
    def test_encode_audio_file_marks_failed_on_nonzero_exit(self, _mock_call):
        media = self._make_audio_media()

        result = media_encoding.encode_audio_file(media.id)

        self.assertEqual(result.encode_status, EncodeStatus.FAILED)
        self.assertTrue(result.encode_error)
        self.assertFalse(result.encoded_file)

    @patch(
        'rockon.bands.services.media_encoding.subprocess.call',
        side_effect=FileNotFoundError('ffmpeg not found'),
    )
    def test_encode_audio_file_handles_missing_binary(self, _mock_call):
        media = self._make_audio_media()

        result = media_encoding.encode_audio_file(media.id)

        self.assertEqual(result.encode_status, EncodeStatus.FAILED)
        self.assertEqual(result.encode_error, 'Encoding tool not available.')

    def test_encode_audio_file_returns_none_for_deleted_media(self):
        result = media_encoding.encode_audio_file(uuid.uuid4())

        self.assertIsNone(result)

    @patch('rockon.bands.services.media_encoding.subprocess.call', return_value=1)
    def test_encode_image_file_marks_failed_on_nonzero_exit(self, _mock_call):
        media = self._make_image_media()

        result = media_encoding.encode_image_file(media.id)

        self.assertEqual(result.encode_status, EncodeStatus.FAILED)
        self.assertTrue(result.encode_error)
        self.assertFalse(result.encoded_file)

    @patch('rockon.bands.services.media_encoding.subprocess.call', return_value=0)
    def test_encode_image_file_marks_done_on_success(self, _mock_call):
        media = self._make_image_media()

        result = media_encoding.encode_image_file(media.id)

        self.assertEqual(result.encode_status, EncodeStatus.DONE)
        self.assertTrue(result.encoded_file)
