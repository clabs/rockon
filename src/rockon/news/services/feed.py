from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from rockon.news.models import NewsPost, PostStatus

_NO_AUDIENCE_SELECTED = Q(
    audience_crew=False, audience_bands=False, audience_exhibitors=False
)
_AUDIENCE_FIELD = {
    'crew': 'audience_crew',
    'bands': 'audience_bands',
    'exhibitors': 'audience_exhibitors',
}


def visible_posts_for_user(user, event, account_context: str | None, limit: int = 20):
    """Return published, due, event- and audience-matching posts, newest first."""
    audience_q = _NO_AUDIENCE_SELECTED
    field = _AUDIENCE_FIELD.get(account_context)
    if field:
        audience_q |= Q(**{field: True})

    qs = (
        NewsPost.objects.filter(
            status=PostStatus.PUBLISHED, publish_at__lte=timezone.now()
        )
        .filter(Q(event__isnull=True) | Q(event=event))
        .filter(audience_q)
        .select_related('event', 'author')
        .order_by('-publish_at')[:limit]
    )
    return list(qs)
