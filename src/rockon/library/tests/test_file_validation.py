from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from rockon.library.file_validation import validate_upload


class ValidateUploadTests(SimpleTestCase):
    def test_accepts_matching_content_type_and_extension(self):
        file = SimpleUploadedFile('photo.png', b'\x89PNG\r\n\x1a\n' + b'\x00' * 16)
        validate_upload(file, {'image/png'})  # does not raise

    def test_rejects_content_type_not_in_allowed_set(self):
        file = SimpleUploadedFile('photo.png', b'\x89PNG\r\n\x1a\n' + b'\x00' * 16)
        with self.assertRaises(ValidationError):
            validate_upload(file, {'application/pdf'})

    def test_rejects_extension_mismatching_sniffed_content(self):
        file = SimpleUploadedFile('photo.jpg', b'\x89PNG\r\n\x1a\n' + b'\x00' * 16)
        with self.assertRaises(ValidationError):
            validate_upload(file, {'image/png'})

    def test_rejects_unrecognized_content(self):
        file = SimpleUploadedFile('script.mp3', b'#!/bin/sh\necho hi\n')
        with self.assertRaises(ValidationError):
            validate_upload(file, {'audio/mpeg'})

    def test_detects_mp3_via_id3_tag(self):
        file = SimpleUploadedFile('track.mp3', b'ID3' + b'\x00' * 16)
        validate_upload(file, {'audio/mpeg'})  # does not raise

    def test_detects_mp3_via_frame_sync(self):
        file = SimpleUploadedFile('track.mp3', b'\xff\xfb\x90\x00' + b'\x00' * 16)
        validate_upload(file, {'audio/mpeg'})  # does not raise

    def test_detects_webp_vs_wav_via_riff_subtype(self):
        webp = SimpleUploadedFile(
            'image.webp', b'RIFF\x00\x00\x00\x00WEBP' + b'\x00' * 8
        )
        wav = SimpleUploadedFile('sound.wav', b'RIFF\x00\x00\x00\x00WAVE' + b'\x00' * 8)

        validate_upload(webp, {'image/webp'})
        validate_upload(wav, {'audio/wav'})

    def test_leaves_file_position_reset_for_later_reads(self):
        file = SimpleUploadedFile('photo.png', b'\x89PNG\r\n\x1a\n' + b'\x00' * 16)
        validate_upload(file, {'image/png'})
        self.assertEqual(file.tell(), 0)
