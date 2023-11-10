from __future__ import annotations

import json
import os

from django.conf import settings
from django.forms import model_to_dict
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

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

    if media.media_type == "audio":
        response = FileResponse(file, status=206)
        response["Accept-Ranges"] = "bytes"
        response["Content-Range"] = f"bytes 0-{file_size-1}/{file_size}"
        return response

    return FileResponse(file, status=200)
