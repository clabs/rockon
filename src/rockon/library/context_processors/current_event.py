from __future__ import annotations

from rockon.base.services import (
    get_current_event_for_request,
    get_request_account_context,
)


def current_event(request):
    event = get_current_event_for_request(request)
    return {
        'current_event': event,
        'current_account_context': get_request_account_context(request),
    }
