from __future__ import annotations

from rockon.base.services import (
    get_current_event_for_request,
    get_open_application_event,
    get_request_account_context,
)


def current_event(request):
    event = get_current_event_for_request(request)

    # Templates call callables on lookup, so the query only runs where the link is rendered.
    def band_application_event():
        return get_open_application_event() or event

    return {
        'current_event': event,
        'current_account_context': get_request_account_context(request),
        'band_application_event': band_application_event,
    }
