from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

# Each entry is (content_type, signature_matcher, allowed_extensions).
# Matching is done on the file's leading bytes only (magic-number
# sniffing). This deliberately avoids a native libmagic dependency
# (python-magic), which segfaults on import on at least one supported
# development platform.
_SIGNATURES: list[tuple[str, Callable[[bytes], bool], set[str]]] = [
    ('image/jpeg', lambda h: h.startswith(b'\xff\xd8\xff'), {'.jpg', '.jpeg'}),
    ('image/png', lambda h: h.startswith(b'\x89PNG\r\n\x1a\n'), {'.png'}),
    ('image/webp', lambda h: h[:4] == b'RIFF' and h[8:12] == b'WEBP', {'.webp'}),
    ('application/pdf', lambda h: h.startswith(b'%PDF-'), {'.pdf'}),
    ('application/postscript', lambda h: h.startswith(b'%!PS'), {'.eps', '.ps'}),
    (
        'audio/mpeg',
        lambda h: (
            h.startswith(b'ID3')
            or (len(h) >= 2 and h[0] == 0xFF and h[1] & 0xE0 == 0xE0)
        ),
        {'.mp3'},
    ),
    ('audio/wav', lambda h: h[:4] == b'RIFF' and h[8:12] == b'WAVE', {'.wav'}),
    ('audio/flac', lambda h: h.startswith(b'fLaC'), {'.flac'}),
    ('audio/ogg', lambda h: h.startswith(b'OggS'), {'.ogg'}),
]


def validate_upload(file: UploadedFile, allowed_content_types: set[str]) -> None:
    """Reject a file whose sniffed content isn't in the allowed set, or
    whose extension doesn't match its sniffed content type.

    Raises django.core.exceptions.ValidationError on rejection.
    """
    file.seek(0)
    header = file.read(64)
    file.seek(0)

    for content_type, matches, extensions in _SIGNATURES:
        if not matches(header):
            continue
        if content_type not in allowed_content_types:
            raise ValidationError(f'File type "{content_type}" is not allowed here.')
        ext = Path(file.name).suffix.lower()
        if ext not in extensions:
            raise ValidationError(
                f'File extension "{ext}" does not match its content ("{content_type}").'
            )
        return

    raise ValidationError('Could not determine a supported file type for this upload.')
