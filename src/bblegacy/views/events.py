from __future__ import annotations

from django.forms import model_to_dict
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

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
