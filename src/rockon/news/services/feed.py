from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from rockon.news.models import NewsPost, PostStatus

_AUDIENCE_FIELD = {
    'crew': 'audience_crew',
    'bands': 'audience_bands',
    'exhibitors': 'audience_exhibitors',
}


def visible_posts_for_user(user, event, account_context: str | None, limit: int = 20):
    """Return published, due, event- and audience-matching posts, newest first.

    Every post must explicitly target at least one audience (enforced by a DB
    constraint), so a user with no resolvable account-context never matches.
    """
    field = _AUDIENCE_FIELD.get(account_context)
    if not field:
        return []

    qs = (
        NewsPost.objects.filter(
            status=PostStatus.PUBLISHED,
            publish_at__lte=timezone.now(),
            **{field: True},
        )
        .filter(Q(event__isnull=True) | Q(event=event))
        .select_related('event', 'author')
        .order_by('-publish_at')[:limit]
    )
    return list(qs)
