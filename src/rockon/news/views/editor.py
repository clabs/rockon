from __future__ import annotations

import json

from django.http import HttpResponse
from django.template import loader
from django.utils.safestring import mark_safe

from rockon.base.models import Event
from rockon.library.decorators import require_group
from rockon.news.models import NewsPost


def _serialize_post(post: NewsPost) -> dict:
    return {
        'id': str(post.id),
        'title': post.title,
        'body_markdown': post.body_markdown,
        'body_html': post.body_html,
        'status': post.status,
        'publish_at': post.publish_at.isoformat() if post.publish_at else None,
        'event': str(post.event_id) if post.event_id else None,
        'event_name': post.event.name if post.event else None,
        'audience_crew': post.audience_crew,
        'audience_bands': post.audience_bands,
        'audience_exhibitors': post.audience_exhibitors,
        'author_name': post.author.get_full_name() or post.author.username
        if post.author
        else None,
        'updated_at': post.updated_at.isoformat(),
    }


@require_group('news_editors')
def editor_home(request):
    posts = NewsPost.objects.select_related('event', 'author').order_by('-created_at')
    events = Event.objects.filter(sub_event_of__isnull=True).order_by('-start')

    template = loader.get_template('news/editor.html')
    extra_context = {
        'site_title': 'News-Editor',
        'posts_json': mark_safe(
            json.dumps([_serialize_post(post) for post in posts], ensure_ascii=False)
        ),
        'events_json': mark_safe(
            json.dumps(
                [{'id': str(event.id), 'name': event.name} for event in events],
                ensure_ascii=False,
            )
        ),
    }
    return HttpResponse(template.render(extra_context, request))
