from __future__ import annotations

from rockon.base.models import Event


def get_event_by_slug(slug: str) -> Event | None:
    """Return event for a slug or None when no event exists."""
    return Event.objects.filter(slug=slug).first()
