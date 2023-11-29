from __future__ import annotations

from rockon.base.models import Event


class SessionCurrentEventMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.session.get(
            "current_event", None
        ):
            request.session["current_event"] = str(Event.get_current_event().id)

        response = self.get_response(request)
        return response
