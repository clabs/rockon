from __future__ import annotations

from rest_framework import routers

from api.views import BandViewSet

router = routers.DefaultRouter()
router.register(r"bands", BandViewSet, basename="bands")
