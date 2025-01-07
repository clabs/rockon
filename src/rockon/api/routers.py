from __future__ import annotations

from rest_framework import routers

from rockon.api.views import (
    BandMediaViewSet,
    BandTrackViewSet,
    BandViewSet,
    BandVoteViewSet,
    CommentViewSet,
)

router = routers.DefaultRouter()
router.register(r"bands", BandViewSet, basename="bands")
router.register(r"band-media", BandMediaViewSet, basename="band-media")
router.register(r"band-votes", BandVoteViewSet, basename="band-votes")
router.register(r"tracks", BandTrackViewSet, basename="tracks")
router.register(r"comments", CommentViewSet, basename="band-comments")
