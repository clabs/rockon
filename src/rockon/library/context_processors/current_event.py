from __future__ import annotations

from rockon.base.models import Event


def current_event(request):
    # Reuse event cached by SessionCurrentEventMiddleware if available
    event = getattr(request, 'current_event', None)
    if event is None:
        event_id = request.session.get('current_event_id')
        if event_id is not None:
            try:
                event = Event.objects.get(id=event_id)
                request.current_event = event
            except Event.DoesNotExist:
                pass
    return {
        'current_event': event,
    }
