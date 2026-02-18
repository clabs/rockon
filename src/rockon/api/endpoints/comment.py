from __future__ import annotations

import uuid

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.comment import CommentIn, CommentOut
from rockon.bands.models import Band, Comment

commentRouter = Router()


def _serialize_comment(comment: Comment) -> dict:
    return {
        'id': str(comment.id),
        'band': str(comment.band_id),
        'user': {
            'first_name': comment.user.first_name,
            'last_name': comment.user.last_name,
        },
        'text': comment.text,
        'reason': comment.reason,
        'mood': comment.mood,
        'created_at': comment.created_at,
        'updated_at': comment.updated_at,
    }


@commentRouter.get(
    '/',
    response=list[CommentOut],
    url_name='comment_list',
    auth=django_auth,
)
def list_comments(request, band: str | None = None):
    """List comments, optionally filtered by band UUID."""
    queryset = Comment.objects.select_related('user').all()
    if band:
        try:
            uuid.UUID(band)
        except ValueError:
            return 400, None
        queryset = queryset.filter(band__id=band)
    return [_serialize_comment(c) for c in queryset]


@commentRouter.post(
    '/',
    response={201: CommentOut},
    url_name='comment_create',
    auth=django_auth,
)
def create_comment(request, data: CommentIn):
    """Create a comment for a band."""
    band = get_object_or_404(Band, id=data.band)
    comment = Comment.objects.create(
        band=band,
        user=request.user,
        text=data.text,
        reason=data.reason,
        mood=data.mood,
    )
    return 201, _serialize_comment(comment)
