from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext as _

# ISO base media "ftyp" brands used by .m4a files from common encoders.
_M4A_BRANDS = {b'M4A ', b'M4B ', b'mp41', b'mp42', b'isom', b'iso2'}

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
    # ADTS frame header: 12-bit sync word, layer bits always 00. Must be
    # checked before MPEG audio, whose frame-sync test also matches it.
    (
        'audio/aac',
        lambda h: len(h) >= 2 and h[0] == 0xFF and h[1] & 0xF6 == 0xF0,
        {'.aac'},
    ),
    (
        'audio/mp4',
        lambda h: h[4:8] == b'ftyp' and h[8:12] in _M4A_BRANDS,
        {'.m4a'},
    ),
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


def allowed_extensions(allowed_content_types: set[str]) -> list[str]:
    """Return the sorted file extensions accepted for the given content types."""
    return sorted(
        ext
        for content_type, _matches, extensions in _SIGNATURES
        if content_type in allowed_content_types
        for ext in extensions
    )


def validate_upload(file: UploadedFile, allowed_content_types: set[str]) -> None:
    """Reject a file whose sniffed content isn't in the allowed set, or
    whose extension doesn't match its sniffed content type.

    Raises django.core.exceptions.ValidationError on rejection.
    """
    file.seek(0)
    header = file.read(64)
    file.seek(0)

    allowed = ', '.join(allowed_extensions(allowed_content_types))
    ext = Path(file.name).suffix.lower()

    for content_type, matches, extensions in _SIGNATURES:
        if not matches(header):
            continue
        if content_type not in allowed_content_types:
            raise ValidationError(
                _('This file type is not allowed here. Allowed: %(allowed)s')
                % {'allowed': allowed}
            )
        if ext not in extensions:
            raise ValidationError(
                _(
                    'The file extension "%(ext)s" does not match the file content. '
                    'Allowed: %(allowed)s'
                )
                % {'ext': ext, 'allowed': allowed}
            )
        return

    raise ValidationError(
        _('The file type could not be recognised. Allowed: %(allowed)s')
        % {'allowed': allowed}
    )
