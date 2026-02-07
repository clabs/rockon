from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist

from rockon.base.models import Event


def is_crewmember(request):
    if getattr(request, 'user') and request.user.is_authenticated:
        event_id = request.session.get('current_event_id')
        if event_id is not None:
            try:
                current_event = Event.objects.get(id=event_id)
                return {'is_crewmember': current_event.crews.is_member(request.user)}
            except ObjectDoesNotExist, AttributeError:
                pass
    return {'is_crewmember': False}
