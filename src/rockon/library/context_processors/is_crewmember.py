from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist

from rockon.base.models import Event


def is_crewmember(request):
    if getattr(request, 'user') and request.user.is_authenticated:
        # Reuse event cached on request by middleware / current_event CP
        current_event = getattr(request, 'current_event', None)
        if current_event is None:
            event_id = request.session.get('current_event_id')
            if event_id is not None:
                try:
                    current_event = Event.objects.get(id=event_id)
                    request.current_event = current_event
                except Event.DoesNotExist:
                    pass
        if current_event is not None:
            try:
                return {'is_crewmember': current_event.crews.is_member(request.user)}
            except (ObjectDoesNotExist, AttributeError):
                pass
    return {'is_crewmember': False}
