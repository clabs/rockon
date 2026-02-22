from __future__ import annotations

from rockon.base.models import Event

SESSION_KEY = 'available_event_ids'


def _calculate_available_event_ids(user):
    """Calculate the list of event IDs the user has access to."""
    if user.is_staff:
        return list(
            Event.objects.filter(sub_event_of__isnull=True)
            .order_by('-start')
            .values_list('id', flat=True)
        )

    event_ids = set()

    current_event = Event.objects.filter(
        is_current=True, sub_event_of__isnull=True
    ).first()
    if current_event:
        event_ids.add(current_event.id)

    if user.groups.filter(name='crew').exists():
        from rockon.crew.models import CrewMember

        crew_events = CrewMember.objects.filter(
            user=user, state__in=['confirmed', 'arrived']
        ).values_list('crew__event_id', flat=True)
        event_ids.update(crew_events)

    if user.groups.filter(name='exhibitors').exists():
        from rockon.exhibitors.models import Exhibitor

        org_ids = user.organisations.values_list('id', flat=True)
        exhibitor_events = (
            Exhibitor.objects.filter(organisation_id__in=org_ids)
            .select_related('event__sub_event_of')
        )

        for exhibitor in exhibitor_events:
            if exhibitor.event.sub_event_of:
                event_ids.add(exhibitor.event.sub_event_of.id)
            else:
                event_ids.add(exhibitor.event_id)

    if user.groups.filter(name='bands').exists():
        from rockon.bands.models import Band

        band_events = Band.objects.filter(band_members__user=user).values_list(
            'event_id', flat=True
        )
        event_ids.update(band_events)

    return list(event_ids)


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
