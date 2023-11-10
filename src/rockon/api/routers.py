from __future__ import annotations

from rest_framework import routers

from rockon.api.views import BandMediaViewSet, BandViewSet

router = routers.DefaultRouter()
router.register(r"bands", BandViewSet, basename="bands")
router.register(r"band-media", BandMediaViewSet, basename="band-media")
