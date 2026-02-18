from __future__ import annotations

from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.track import TrackOut
from rockon.bands.models import Track

trackRouter = Router()


@trackRouter.get(
    '/',
    response=list[TrackOut],
    url_name='track_list',
    auth=django_auth,
)
def list_tracks(request, event: str | None = None):
    """List active tracks, optionally filtered by event slug."""
    queryset = Track.objects.filter(active=True)
    if event:
        queryset = queryset.filter(events__slug__icontains=event)
    return [
        {
            'id': str(t.id),
            'name': t.name,
            'slug': t.slug,
            'active': t.active,
            'created_at': t.created_at,
            'updated_at': t.updated_at,
        }
        for t in queryset
    ]
