from __future__ import annotations

import os
import re
import string

from django.conf import settings
from django.http import FileResponse, JsonResponse

_ALLOWED_FILENAME_CHARS = frozenset(string.ascii_letters + string.digits + '._-')


def _is_safe_filename(filename: str) -> bool:
    # Must not be empty and must not start with a dot (prevents hidden/traversal names).
    if not filename or filename.startswith('.'):
        return False
    # Path separators are forbidden regardless of OS.
    if '/' in filename or '\\' in filename:
        return False
    # Must have at least one dot (i.e. an extension).
    if '.' not in filename:
        return False
    return all(c in _ALLOWED_FILENAME_CHARS for c in filename)


def streaming_download(request, band, filename):
    if not _is_safe_filename(filename):
        return JsonResponse({'message': 'Invalid filename'}, status=400)

    base_dir = os.path.realpath(os.path.join(settings.MEDIA_ROOT, 'bids', str(band)))
    file_path = os.path.realpath(os.path.join(base_dir, filename))

    if not file_path.startswith(base_dir + os.sep):
        return JsonResponse({'message': 'Invalid file path'}, status=400)

    try:
        file_size = os.path.getsize(file_path)
        file = open(file_path, 'rb')  # FileResponse takes ownership and closes the file
    except FileNotFoundError:
        return JsonResponse({'message': 'File not found'}, status=404)
    except OSError:
        # Handle other access-related errors (e.g., PermissionError, IsADirectoryError)
        return JsonResponse({'message': 'Unable to access file'}, status=403)

    if filename.endswith('.mp3'):
        range_header = request.META.get('HTTP_RANGE')
        if range_header:
            match = re.match(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else file_size - 1
                end = min(end, file_size - 1)
                # Validate the requested range; return 416 if invalid.
                if start < 0 or start >= file_size or start > end:
                    file.close()
                    response = JsonResponse({'message': 'Range Not Satisfiable'}, status=416)
                    response['Content-Range'] = f'bytes */{file_size}'
                    return response
                length = end - start + 1
                file.seek(start)
                response = FileResponse(
                    file,
                    status=206,
                    content_type='audio/mpeg',
                )
                response['Content-Length'] = length
                response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                response['Accept-Ranges'] = 'bytes'
                return response
        response = FileResponse(file, status=200, content_type='audio/mpeg')
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = file_size
        return response

    if filename.endswith('.webp'):
        response = FileResponse(file, status=200)
        response['Content-Type'] = 'image/webp'
        return response

    return FileResponse(file, status=200)
