from __future__ import annotations

from rockon.base.models import Event


class SessionCurrentEventMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authenticated = request.user.is_authenticated
        event_not_set = not request.session.get('current_event_id', None)

        if authenticated and event_not_set:
            current_event = Event.get_current_event()
            if current_event:
                request.session['current_event_id'] = str(current_event.id)
                request.session['current_event_slug'] = current_event.slug
                request.current_event = current_event

        response = self.get_response(request)
        return response
