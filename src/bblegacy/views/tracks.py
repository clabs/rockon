from __future__ import annotations

import json

from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bblegacy.bearer_token_auth import bearer_token_required, test_bearer_token
from bblegacy.models import Track


@csrf_exempt
@bearer_token_required
@require_http_methods(["POST", "GET", "DELETE"])
def track_handler(request, track_id: str = None):
    if request.method == "GET":
        tracks = Track.objects.all()
        _tracks = [model_to_dict(track) for track in tracks]
        return JsonResponse({"tracks": _tracks}, status=200)

    if request.method == "POST":
        if not test_bearer_token(request.headers.get("Authorization"), role="admin"):
            return JsonResponse({"message": "Unauthorized"}, status=401)
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        try:
            track = Track.create_from_json(body)
        except Exception:
            return JsonResponse({"message": "Something went wrong"}, status=400)

        return JsonResponse({"tracks": model_to_dict(track)}, status=201)

    if request.method == "DELETE":
        try:
            Track.objects.get(id=track_id).delete()
        except Track.DoesNotExist:
            pass

        return JsonResponse({"message": "Track deleted"}, status=200)
