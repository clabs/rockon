from __future__ import annotations

import json
import os

from django.conf import settings
from django.forms import model_to_dict
from django.forms.models import model_to_dict
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bblegacy.models import Media


@csrf_exempt
@require_http_methods(["POST"])
def new_media_handler(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=400)

    try:
        media = Media.create_from_json(body)
    except Exception:
        return JsonResponse({"message": "Something went wrong"}, status=400)

    _media = model_to_dict(media)

    return JsonResponse({"media": _media}, status=201)


@csrf_exempt
@require_http_methods(["DELETE", "PUT"])
def media_handler(request, media_id):
    if request.method == "DELETE":
        Media.remove(media_id)
        return JsonResponse({"message": "Media deleted"}, status=200)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=400)

    try:
        media = Media.objects.get(id=media_id)
    except Media.DoesNotExist:
        return JsonResponse({"message": "Media not found"}, status=404)

    if request.method == "PUT":
        media.update_from_json(body)
        return JsonResponse({"media": model_to_dict(media)}, status=200)


def serve_media(request, bid_id, media_id, serve_thumbnail: bool = False):
    if media_id.endswith("_small"):
        media_id = media_id.split("_small")[0]
        serve_thumbnail = True

    try:
        media = Media.objects.get(id=media_id)
    except Media.DoesNotExist:
        return JsonResponse({"message": "Media not found"}, status=404)

    path = os.path.join(settings.MEDIA_ROOT, "bids", media.bid.id)

    if serve_thumbnail:
        media.filename = (
            f"{media.filename.split('.')[0]}_small.{media.filename.split('.')[-1]}"
        )

    try:
        file_path = os.path.join(path, media.filename)
        file = open(file_path, "rb")
        file_size = os.path.getsize(file_path)
    except FileNotFoundError:
        return JsonResponse({"message": "File not found"}, status=404)

    if media.type == "audio":
        response = FileResponse(file, status=206)
        response["Accept-Ranges"] = "bytes"
        response["Content-Range"] = f"bytes 0-{file_size-1}/{file_size}"
        return response

    return FileResponse(file, status=200)
