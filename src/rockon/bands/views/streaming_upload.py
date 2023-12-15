from __future__ import annotations

import os

from django.conf import settings
from django.http import FileResponse, JsonResponse

from rockon.bands.models import BandMedia


def streaming_upload(request, band, filename):
    path = os.path.join(settings.MEDIA_ROOT, "bids", band)

    try:
        file_path = os.path.join(path, filename)
        file = open(file_path, "rb")
        file_size = os.path.getsize(file_path)
    except FileNotFoundError:
        return JsonResponse({"message": "File not found"}, status=404)

    lookup = f"bids/{band}/{filename}"
    media = BandMedia.objects.get(file=lookup)

    serve_encoded = request.GET.get("encoded", False)
    if serve_encoded and media.encoded_file:
        file = open(media.encoded_file.path, "rb")
        file_size = os.path.getsize(media.encoded_file.path)

    if (
        media.media_type == "press_photo" or media.media_type == "logo"
    ) and serve_encoded:
        response = FileResponse(file, status=200)
        response["Content-Type"] = "image/png"
        return response

    if media.media_type == "audio":
        response = FileResponse(file, status=206)
        response["Accept-Ranges"] = "bytes"
        response["Content-Range"] = f"bytes 0-{file_size-1}/{file_size}"
        return response

    return FileResponse(file, status=200)
