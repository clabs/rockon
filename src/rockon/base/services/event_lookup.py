from __future__ import annotations

import re
from typing import Optional
from urllib.parse import quote

from django.contrib.auth.models import AnonymousUser

from rockon.base.models import Event

SUPPORTED_ACCOUNT_CONTEXTS = ('crew', 'bands', 'exhibitors')
EVENT_PATH_RE = re.compile(r'/event/(?P<slug>[^/]+)/')


def get_event_by_slug(slug: str) -> Optional[Event]:
    """Return event for a slug or None when no event exists."""
    return Event.objects.filter(slug=slug).first()


def get_selectable_event_by_slug(slug: str) -> Optional[Event]:
    """Return a top-level event that can be selected in the event switcher."""
    return Event.objects.filter(slug=slug, sub_event_of__isnull=True).first()


def get_root_event(event: Optional[Event]) -> Optional[Event]:
    """Normalize sub-events to their top-level parent event."""
    if event is None:
        return None
    return event.sub_event_of or event


def calculate_available_event_ids(user) -> list:
    """Calculate top-level event IDs the user can access."""
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
            user=user, state='confirmed'
        ).values_list('crew__event_id', flat=True)
        event_ids.update(crew_events)

    if user.groups.filter(name='exhibitors').exists():
        from rockon.exhibitors.models import Exhibitor

        org_ids = user.organisations.values_list('id', flat=True)
        exhibitor_events = Exhibitor.objects.filter(
            organisation_id__in=org_ids
        ).select_related('event__sub_event_of')

        for exhibitor in exhibitor_events:
            root_event = get_root_event(exhibitor.event)
            if root_event is not None:
                event_ids.add(root_event.id)

    if user.groups.filter(name='bands').exists():
        from rockon.bands.models import Band

        band_events = Band.objects.filter(band_members__user=user).values_list(
            'event_id', flat=True
        )
        event_ids.update(band_events)

    return list(event_ids)


def get_available_events(user):
    """Return accessible top-level events ordered newest first."""
    event_ids = calculate_available_event_ids(user)
    if not event_ids:
        return Event.objects.none()
    return Event.objects.filter(id__in=event_ids, sub_event_of__isnull=True).order_by(
        '-start'
    )


def get_default_event() -> Optional[Event]:
    """Return the global fallback event when no user-specific choice exists."""
    return Event.get_current_event() or Event.objects.order_by('start').first()


def get_fallback_event_for_user(user) -> Optional[Event]:
    """Return the event to use on non-event pages."""
    if user and not isinstance(user, AnonymousUser) and user.is_authenticated:
        event = get_available_events(user).first()
        if event is not None:
            return event
    return get_default_event()


def get_request_path_event_slug(request) -> Optional[str]:
    """Return the event slug from the resolved route when available."""
    resolver_match = getattr(request, 'resolver_match', None)
    if resolver_match is None:
        return None
    slug = resolver_match.kwargs.get('slug')
    if isinstance(slug, str) and slug:
        return slug
    return None


def get_current_event_for_request(request) -> Optional[Event]:
    """Resolve the current event from the request URL, falling back on global pages."""
    cached_event = getattr(request, 'current_event', None)
    if cached_event is not None:
        return cached_event

    slug = get_request_path_event_slug(request)
    if slug:
        event = get_root_event(get_event_by_slug(slug))
    else:
        event = get_fallback_event_for_user(getattr(request, 'user', None))

    request.current_event = event
    return event


def get_request_account_context(request) -> Optional[str]:
    """Infer the account context for default event landing pages."""
    explicit_context = request.GET.get('ctx')
    if explicit_context in SUPPORTED_ACCOUNT_CONTEXTS:
        return explicit_context

    resolver_match = getattr(request, 'resolver_match', None)
    if resolver_match and resolver_match.namespace in SUPPORTED_ACCOUNT_CONTEXTS:
        return resolver_match.namespace

    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return None

    for context in SUPPORTED_ACCOUNT_CONTEXTS:
        if user.groups.filter(name=context).exists():
            return context

    return None


def get_event_slug_for_path(event: Event, path: str) -> str:
    """Return the route slug to use for a target event on a given path."""
    if '/exhibitors/' not in path:
        return event.slug

    sub_event = event.sub_events.order_by('start').first()
    if sub_event is not None:
        return sub_event.slug
    return event.slug


def get_path_event_slug(path: str) -> str | None:
    """Extract the event slug from an event-scoped path."""
    match = EVENT_PATH_RE.search(path)
    if match is None:
        return None
    return match.group('slug')


def replace_event_slug_in_path(path: str, new_slug: str) -> str:
    """Replace the event slug in a path while preserving the remaining route."""
    current_slug = get_path_event_slug(path)
    if current_slug is None or current_slug == new_slug:
        return path

    slug_re = re.compile(r'^[A-Za-z0-9_-]+$')
    if slug_re.fullmatch(new_slug):
        new_slug_safe = new_slug
    else:
        new_slug_safe = quote(new_slug, safe='-_')

    return EVENT_PATH_RE.sub(f'/event/{new_slug_safe}/', path, count=1)


def build_switched_event_path(path: str, event: Event) -> str:
    """Return a path for the same event-scoped view using a different event."""
    target_slug = get_event_slug_for_path(event, path)
    return replace_event_slug_in_path(path, target_slug)
