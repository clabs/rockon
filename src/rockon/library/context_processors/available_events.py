from __future__ import annotations

from rockon.base.models import Event
from rockon.base.services import calculate_available_event_ids

SESSION_KEY = 'available_event_ids'


def _calculate_available_event_ids(user):
    """Calculate the list of event IDs the user has access to."""
    return calculate_available_event_ids(user)


def clear_available_events_cache(request):
    """Clear the cached available events from the session."""
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]


def available_events(request):
    """
    Provide available events for event context switching.

    - Staff users can see all events
    - Crew members can see events they have membership for
    - Exhibitors can see events their organisation was an exhibitor at

    Results are cached in the session for performance.
    """
    if not request.user.is_authenticated:
        return {'available_events': [], 'can_switch_events': False}

    user = request.user

    cached_ids = request.session.get(SESSION_KEY)

    if cached_ids is None:
        cached_ids = _calculate_available_event_ids(user)
        request.session[SESSION_KEY] = [str(eid) for eid in cached_ids]

    if cached_ids:
        events = Event.objects.filter(
            id__in=cached_ids, sub_event_of__isnull=True
        ).order_by('-start')
    else:
        events = Event.objects.none()

    return {
        'available_events': events,
        'can_switch_events': events.count() > 1
        or (events.count() == 1 and user.is_staff),
    }
