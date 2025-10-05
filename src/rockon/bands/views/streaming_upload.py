from __future__ import annotations

import os

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
        response = FileResponse(file, status=206)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Range'] = f'bytes 0-{file_size - 1}/{file_size}'
        return response

    if filename.endswith('.webp'):
        response = FileResponse(file, status=200)
        response['Content-Type'] = 'image/webp'
        return response

    return FileResponse(file, status=200)
