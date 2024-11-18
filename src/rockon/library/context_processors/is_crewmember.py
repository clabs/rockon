from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist

from rockon.base.models import Event


def is_crewmember(request):
    if request.user.is_authenticated:
        event_id = request.session.get("current_event_id")
        if event_id is not None:
            try:
                current_event = Event.objects.get(id=event_id)
                if current_event.crews.exists():
                    is_member = current_event.crews.is_member(request.user)
                    return {"is_crewmember": is_member}
            except (ObjectDoesNotExist, AttributeError):
                pass
    return {"is_crewmember": False}
