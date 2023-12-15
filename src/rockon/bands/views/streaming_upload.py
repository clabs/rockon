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

    serve_encoded = False
    endings = ["-thumbnail.png", "-encoded.mp3"]
    if filename.endswith(tuple(endings)):
        serve_encoded = True
        for ending in endings:
            filename = filename.replace(ending, "")

    lookup = f"bids/{band}/{filename}"
    media = BandMedia.objects.get(file__startswith=lookup)

    if serve_encoded:
        file = open(media.encoded_file.path, "rb")
        file_size = os.path.getsize(media.encoded_file.path)

    if media.media_type == "audio":
        response = FileResponse(file, status=206)
        response["Accept-Ranges"] = "bytes"
        response["Content-Range"] = f"bytes 0-{file_size-1}/{file_size}"
        return response

    return FileResponse(file, status=200)
