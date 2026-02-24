from __future__ import annotations

import os
import re

from django.conf import settings
from django.http import FileResponse, JsonResponse


def streaming_upload(request, band, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'bids', band)

    try:
        file_path = os.path.join(path, filename)
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
