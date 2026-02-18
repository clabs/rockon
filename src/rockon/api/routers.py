from __future__ import annotations

from rest_framework import routers

from rockon.api.views import (
    BandMediaViewSet,
    BandTrackViewSet,
    CommentViewSet,
)

router = routers.DefaultRouter()
router.register(r'band-media', BandMediaViewSet, basename='band-media')
router.register(r'tracks', BandTrackViewSet, basename='tracks')
router.register(r'comments', CommentViewSet, basename='band-comments')
