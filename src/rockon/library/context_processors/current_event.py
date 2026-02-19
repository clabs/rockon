from __future__ import annotations

from rockon.base.models import Event


def current_event(request):
    event_id = request.session.get('current_event_id')
    event = None
    if event_id is not None:
        try:
            event = Event.objects.get(id=event_id)
            # Cache on request so other context processors avoid a duplicate query
            request._current_event_cache = event
        except Event.DoesNotExist:
            pass
    return {
        'current_event': event,
    }
