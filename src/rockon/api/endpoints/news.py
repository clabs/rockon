from __future__ import annotations

from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.news import (
    NewsPostCreateIn,
    NewsPostOut,
    NewsPostPatchIn,
    NewsPreviewIn,
    NewsPreviewOut,
)
from rockon.base.models import Event
from rockon.news.models import NewsPost, PostStatus
from rockon.news.services.rendering import render_markdown_to_html

newsRouter = Router()


def _check_news_editor(request):
    return (
        request.user.is_staff
        or request.user.groups.filter(name='news_editors').exists()
    )


def _serialize_news_post(post: NewsPost) -> dict:
    return {
        'id': str(post.id),
        'title': post.title,
        'slug': post.slug,
        'body_markdown': post.body_markdown,
        'body_html': post.body_html,
        'status': post.status,
        'publish_at': post.publish_at,
        'event': str(post.event_id) if post.event_id else None,
        'event_name': post.event.name if post.event else None,
        'audience_crew': post.audience_crew,
        'audience_bands': post.audience_bands,
        'audience_exhibitors': post.audience_exhibitors,
        'author_name': post.author.get_full_name() or post.author.username
        if post.author
        else None,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
    }


def _finalize_post(post: NewsPost) -> None:
    """Re-render markdown and auto-fill publish_at once fields are set."""
    post.body_html = render_markdown_to_html(post.body_markdown)
    # Publishing without an explicit publish_at means "publish now".
    if post.status == PostStatus.PUBLISHED and post.publish_at is None:
        post.publish_at = timezone.now()


@newsRouter.get(
    '/',
    response={200: list[NewsPostOut], 403: list[NewsPostOut]},
    url_name='news_list',
    auth=django_auth,
)
def list_news_posts(request, event: str | None = None, status: str | None = None):
    if not _check_news_editor(request):
        return 403, []
    qs = NewsPost.objects.select_related('event', 'author').all()
    if event:
        qs = qs.filter(event__slug=event)
    if status:
        qs = qs.filter(status=status)
    return [_serialize_news_post(post) for post in qs]


@newsRouter.post(
    '/preview/',
    response={200: NewsPreviewOut, 403: None},
    url_name='news_preview',
    auth=django_auth,
)
def preview_news_post(request, data: NewsPreviewIn):
    if not _check_news_editor(request):
        return 403, None
    return 200, {'body_html': render_markdown_to_html(data.body_markdown)}


@newsRouter.get(
    '/{post_id}/',
    response={200: NewsPostOut, 403: None, 404: None},
    url_name='news_detail',
    auth=django_auth,
)
def get_news_post(request, post_id: str):
    if not _check_news_editor(request):
        return 403, None
    post = get_object_or_404(
        NewsPost.objects.select_related('event', 'author'), id=post_id
    )
    return 200, _serialize_news_post(post)


@newsRouter.post(
    '/',
    response={201: NewsPostOut, 403: None},
    url_name='news_create',
    auth=django_auth,
)
def create_news_post(request, data: NewsPostCreateIn):
    if not _check_news_editor(request):
        return 403, None
    post = NewsPost(
        author=request.user,
        title=data.title,
        body_markdown=data.body_markdown,
        status=data.status,
        publish_at=data.publish_at,
        event=get_object_or_404(Event, id=data.event) if data.event else None,
        audience_crew=data.audience_crew,
        audience_bands=data.audience_bands,
        audience_exhibitors=data.audience_exhibitors,
    )
    _finalize_post(post)
    post.save()
    return 201, _serialize_news_post(post)


@newsRouter.patch(
    '/{post_id}/',
    response={200: NewsPostOut, 403: None, 404: None},
    url_name='news_patch',
    auth=django_auth,
)
def patch_news_post(request, post_id: str, data: NewsPostPatchIn):
    if not _check_news_editor(request):
        return 403, None
    post = get_object_or_404(NewsPost, id=post_id)

    if data.title is not None:
        post.title = data.title
    if data.body_markdown is not None:
        post.body_markdown = data.body_markdown
    if data.status is not None:
        post.status = data.status
    if data.publish_at is not None:
        post.publish_at = data.publish_at
    if data.event is not None:
        post.event = get_object_or_404(Event, id=data.event)
    if data.audience_crew is not None:
        post.audience_crew = data.audience_crew
    if data.audience_bands is not None:
        post.audience_bands = data.audience_bands
    if data.audience_exhibitors is not None:
        post.audience_exhibitors = data.audience_exhibitors

    _finalize_post(post)
    post.save()
    post = NewsPost.objects.select_related('event', 'author').get(id=post.id)
    return 200, _serialize_news_post(post)


@newsRouter.delete(
    '/{post_id}/',
    response={204: None, 403: None, 404: None},
    url_name='news_delete',
    auth=django_auth,
)
def delete_news_post(request, post_id: str):
    if not _check_news_editor(request):
        return 403, None
    post = get_object_or_404(NewsPost, id=post_id)
    post.delete()
    return 204, None
