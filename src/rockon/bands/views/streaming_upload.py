from __future__ import annotations

import os
import re

from django.conf import settings
from django.http import FileResponse, JsonResponse


# Only allow filenames that are a single safe name with one extension (no path separators or traversal).
_SAFE_FILENAME_RE = re.compile(r'[\w\-]+\.[\w]+$')


def streaming_upload(request, band, filename):
    if not _SAFE_FILENAME_RE.match(filename):
        return JsonResponse({'message': 'Invalid filename'}, status=400)

    base_dir = os.path.realpath(os.path.join(settings.MEDIA_ROOT, 'bids', str(band)))
    file_path = os.path.realpath(os.path.join(base_dir, filename))

    if not file_path.startswith(base_dir + os.sep):
        return JsonResponse({'message': 'Invalid file path'}, status=400)

    try:
        file = open(file_path, 'rb')
        file_size = os.path.getsize(file_path)
    except FileNotFoundError:
        return JsonResponse({'message': 'File not found'}, status=404)

    if filename.endswith('.mp3'):
        range_header = request.META.get('HTTP_RANGE')
        if range_header:
            match = re.match(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else file_size - 1
                end = min(end, file_size - 1)
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
