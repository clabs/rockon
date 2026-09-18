from __future__ import annotations

import logging
import os
import subprocess

from django.conf import settings

from rockon.bands.models.band_media import BandMedia, EncodeStatus

logger = logging.getLogger(__name__)


def _encode_error_message(exc: Exception) -> str:
    if isinstance(exc, OSError):
        return 'Encoding tool not available.'
    return 'Encoding failed for uploaded file.'


def _relative_encoded_path(file_path: str, new_file_name: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.relpath(file_path, start=settings.MEDIA_ROOT)),
        new_file_name,
    )


def encode_audio_file(id) -> BandMedia | None:
    """Encode an uploaded audio file to mp3 via ffmpeg."""
    try:
        _file = BandMedia.objects.get(id=id)
    except BandMedia.DoesNotExist:
        logger.warning('BandMedia %s no longer exists; skipping audio encode.', id)
        return None
    if not _file.file:
        return _file

    file_name = os.path.basename(_file.file.name)
    file_name_without_extension = ''.join(file_name.split('.')[:-1])
    new_file_name = f'{file_name_without_extension}-encoded.mp3'
    new_absolute_path = os.path.abspath(
        os.path.join(os.path.dirname(_file.file.path), new_file_name)
    )

    ffmpeg_cmd = [
        settings.FFMPEG_BIN,
        '-y',
        '-hide_banner',
        '-i',
        _file.file.path,
        '-vn',
        '-c:a',
        'libmp3lame',
        '-b:a',
        '128k',
        '-ar',
        '44100',
        new_absolute_path,
    ]
    try:
        return_code = subprocess.call(ffmpeg_cmd)
        if return_code != 0:
            raise RuntimeError(f'ffmpeg exited with code {return_code}')
    except (OSError, RuntimeError) as exc:
        logger.exception(
            'Audio encode failed for BandMedia %s (band %s)', id, _file.band_id
        )
        _file.encode_status = EncodeStatus.FAILED
        _file.encode_error = _encode_error_message(exc)
        _file.save()
        return _file

    _file.encoded_file = _relative_encoded_path(_file.file.path, new_file_name)
    _file.encode_status = EncodeStatus.DONE
    _file.save()

    return _file


def encode_image_file(id) -> BandMedia | None:
    """Encode an uploaded image file to a webp thumbnail via ImageMagick."""
    try:
        _file = BandMedia.objects.get(id=id)
    except BandMedia.DoesNotExist:
        logger.warning('BandMedia %s no longer exists; skipping image encode.', id)
        return None
    if not _file.file:
        return _file

    file_name = os.path.basename(_file.file.name)
    file_name_without_extension = ''.join(file_name.split('.')[:-1])
    new_file_name = f'{file_name_without_extension}-thumbnail.webp'
    new_absolute_path = os.path.abspath(
        os.path.join(os.path.dirname(_file.file.path), new_file_name)
    )

    convert_cmd = [
        settings.CONVERT_BIN,
        _file.file.path,
        '-quality',
        '70%',
        '-resize',
        '310x',
        new_absolute_path,
    ]
    try:
        return_code = subprocess.call(convert_cmd)
        if return_code != 0:
            raise RuntimeError(f'convert exited with code {return_code}')
    except (OSError, RuntimeError) as exc:
        logger.exception(
            'Image encode failed for BandMedia %s (band %s)', id, _file.band_id
        )
        _file.encode_status = EncodeStatus.FAILED
        _file.encode_error = _encode_error_message(exc)
        _file.save()
        return _file

    _file.encoded_file = _relative_encoded_path(_file.file.path, new_file_name)
    _file.encode_status = EncodeStatus.DONE
    _file.save()

    return _file
