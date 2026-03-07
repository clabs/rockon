from __future__ import annotations

import time
import uuid
from unittest.mock import mock_open, patch

from django.test import RequestFactory, TestCase

from rockon.bands.views.streaming_upload import _is_safe_filename, streaming_upload


class SafeFilenameTests(TestCase):
    def test_valid_single_dot(self):
        self.assertTrue(_is_safe_filename('song.mp3'))

    def test_valid_multi_dot(self):
        self.assertTrue(_is_safe_filename('my.band.song.mp3'))

    def test_valid_with_dash_and_underscore(self):
        self.assertTrue(_is_safe_filename('my-band_file.webp'))

    def test_rejects_path_separator_slash(self):
        self.assertFalse(_is_safe_filename('foo/bar.mp3'))

    def test_rejects_path_separator_backslash(self):
        self.assertFalse(_is_safe_filename('foo\\bar.mp3'))

    def test_rejects_traversal(self):
        self.assertFalse(_is_safe_filename('../etc/passwd'))

    def test_rejects_leading_dot(self):
        self.assertFalse(_is_safe_filename('.hidden.mp3'))

    def test_rejects_no_dot(self):
        self.assertFalse(_is_safe_filename('songmp3'))

    def test_rejects_empty(self):
        self.assertFalse(_is_safe_filename(''))

    def test_rejects_space(self):
        self.assertFalse(_is_safe_filename('my song.mp3'))

    def test_rejects_dollar_sign(self):
        self.assertFalse(_is_safe_filename('song$.mp3'))

    def test_rejects_null_byte(self):
        self.assertFalse(_is_safe_filename('song\x00.mp3'))

    def test_redos_regression_no_hang(self):
        # A long string of dashes with no dot was the ReDoS trigger for the old regex.
        # It must be rejected quickly (well under 1 second).
        malicious = 'a-' * 5000 + 'a'
        start = time.monotonic()
        result = _is_safe_filename(malicious)
        elapsed = time.monotonic() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 1.0)


class StreamingUploadViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.band = uuid.uuid4()

    def _get(self, filename, **meta):
        return self.factory.get(f'/uploads/bids/{self.band}/{filename}', **meta)

    def test_invalid_filename_returns_400(self):
        request = self._get('../bad.mp3')
        response = streaming_upload(request, self.band, '../bad.mp3')
        self.assertEqual(response.status_code, 400)

    def test_no_extension_returns_400(self):
        request = self._get('noextension')
        response = streaming_upload(request, self.band, 'noextension')
        self.assertEqual(response.status_code, 400)

    def test_file_not_found_returns_404(self):
        request = self._get('song.mp3')
        with (
            patch(
                'rockon.bands.views.streaming_upload.os.path.realpath',
                side_effect=lambda p: p,
            ),
            patch('rockon.bands.views.streaming_upload.settings.MEDIA_ROOT', '/media'),
            patch('builtins.open', side_effect=FileNotFoundError),
        ):
            response = streaming_upload(request, self.band, 'song.mp3')
        self.assertEqual(response.status_code, 404)

    def test_mp3_returns_200(self):
        filename = 'song.mp3'
        request = self._get(filename)
        m = mock_open(read_data=b'data')
        with (
            patch('rockon.bands.views.streaming_upload.settings.MEDIA_ROOT', '/media'),
            patch(
                'rockon.bands.views.streaming_upload.os.path.realpath',
                side_effect=lambda p: p.replace('\\', '/'),
            ),
            patch('rockon.bands.views.streaming_upload.os.sep', '/'),
            patch(
                'rockon.bands.views.streaming_upload.os.path.getsize', return_value=4
            ),
            patch('builtins.open', m),
        ):
            response = streaming_upload(request, self.band, filename)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'audio/mpeg')

    def test_mp3_range_request_returns_206(self):
        filename = 'song.mp3'
        request = self._get(filename, HTTP_RANGE='bytes=0-1')
        m = mock_open(read_data=b'data')
        with (
            patch('rockon.bands.views.streaming_upload.settings.MEDIA_ROOT', '/media'),
            patch(
                'rockon.bands.views.streaming_upload.os.path.realpath',
                side_effect=lambda p: p.replace('\\', '/'),
            ),
            patch('rockon.bands.views.streaming_upload.os.sep', '/'),
            patch(
                'rockon.bands.views.streaming_upload.os.path.getsize', return_value=4
            ),
            patch('builtins.open', m),
        ):
            response = streaming_upload(request, self.band, filename)
        self.assertEqual(response.status_code, 206)
        self.assertEqual(response['Content-Range'], 'bytes 0-1/4')

    def test_webp_returns_200(self):
        filename = 'cover.webp'
        request = self._get(filename)
        m = mock_open(read_data=b'data')
        with (
            patch('rockon.bands.views.streaming_upload.settings.MEDIA_ROOT', '/media'),
            patch(
                'rockon.bands.views.streaming_upload.os.path.realpath',
                side_effect=lambda p: p.replace('\\', '/'),
            ),
            patch('rockon.bands.views.streaming_upload.os.sep', '/'),
            patch(
                'rockon.bands.views.streaming_upload.os.path.getsize', return_value=4
            ),
            patch('builtins.open', m),
        ):
            response = streaming_upload(request, self.band, filename)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/webp')

    def test_multidot_filename_accepted(self):
        filename = 'my.band.song.mp3'
        request = self._get(filename)
        m = mock_open(read_data=b'data')
        with (
            patch('rockon.bands.views.streaming_upload.settings.MEDIA_ROOT', '/media'),
            patch(
                'rockon.bands.views.streaming_upload.os.path.realpath',
                side_effect=lambda p: p.replace('\\', '/'),
            ),
            patch('rockon.bands.views.streaming_upload.os.sep', '/'),
            patch(
                'rockon.bands.views.streaming_upload.os.path.getsize', return_value=4
            ),
            patch('builtins.open', m),
        ):
            response = streaming_upload(request, self.band, filename)
        self.assertEqual(response.status_code, 200)
