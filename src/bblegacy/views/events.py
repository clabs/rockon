from __future__ import annotations

import json

import dateparser
from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pyexpat import model

from bblegacy.bearer_token_auth import (
    bearer_token_admin,
    bearer_token_required,
    test_bearer_token,
)
from bblegacy.models import Event, Track


@require_http_methods(["GET"])
def event_list(request):
    events = Event.objects.all()
    _events = [
        model_to_dict(
            event, fields=["name", "opening_date", "closing_date", "id", "created"]
        )
        for event in events
    ]
    tracks = Track.objects.all().values("name", "event", "visible", "id", "created")
    data = {
        "events": list(_events),
        "tracks": list(tracks),
    }
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["PUT", "GET", "POST"])
def event_handler(request, event_id: str = None):
    if request.method == "POST":
        return JsonResponse({"message": "Method not yet implemented"}, status=405)

    if request.method == "GET":
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                _event = model_to_dict(event)
                _tracks = Track.objects.all().values(
                    "name", "event", "visible", "id", "created"
                )
                return JsonResponse(
                    {"tracks": list(_tracks), "events": list(_event)}, status=200
                )
            except Exception:
                return JsonResponse({"message": "Something went wrong"}, status=400)
        events = Event.objects.all()
        _events = [model_to_dict(event) for event in events]
        tracks = Track.objects.all().values("name", "event", "visible", "id", "created")
        response = {
            "events": list(_events),
            "tracks": list(tracks),
        }
        return JsonResponse(response, status=200)

    if request.method == "PUT":
        if not test_bearer_token(request.headers.get("Authorization"), role="admin"):
            return JsonResponse({"message": "Unauthorized"}, status=401)
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        body["opening_date"] = dateparser.parse(body["opening_date"])
        body["closing_date"] = dateparser.parse(body["closing_date"])

        event = Event.objects.get(id=event_id)
        event = event.update_from_json(body)

        _event = model_to_dict(event)
        _tracks = Track.objects.all().values(
            "name", "event", "visible", "id", "created"
        )
        return JsonResponse(
            {"tracks": list(_tracks), "events": list(_event)}, status=200
        )
