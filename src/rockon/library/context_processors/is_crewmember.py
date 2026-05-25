from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist

from rockon.base.services import get_current_event_for_request


def is_crewmember(request):
    if getattr(request, 'user') and request.user.is_authenticated:
        current_event = get_current_event_for_request(request)
        if current_event is not None:
            try:
                return {'is_crewmember': current_event.crews.is_member(request.user)}
            except ObjectDoesNotExist, AttributeError:
                pass
    return {'is_crewmember': False}
