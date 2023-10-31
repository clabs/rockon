from __future__ import annotations

import json

import dateparser
from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bblegacy.bearer_token_auth import (
    bearer_token_admin,
    bearer_token_required,
    test_bearer_token,
)
from bblegacy.models import Event, Track


@csrf_exempt
@require_http_methods(["PUT", "GET", "POST"])
def event_handler(request, event_id: str = None):
    if request.method == "POST":
        return JsonResponse({"message": "Method not yet implemented"}, status=405)

    if request.method == "GET":
        events = Event.objects.all()
        tracks = Track.objects.all()
        # if event_id:
        #     try:
        #         event = Event.objects.get(id=event_id)
        #         filter_event = event
        #         events = [events.filter(id=event_id)]
        #     except Exception:
        #         return JsonResponse({"message": "Something went wrong"}, status=400)

        _event_response_list = []

        _events = [model_to_dict(event) for event in events]

        for event in _events:
            event["tracks"] = list(
                tracks.filter(event=event["id"]).values_list("id", flat=True)
            )
            _event_response_list.append(event)

        _tracks = [model_to_dict(track) for track in tracks]

        response = {
            "tracks": _tracks,
            "events": _event_response_list,
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
