from __future__ import annotations

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/bands/(?P<band_id>[0-9a-f-]+)/reactions/$',
        consumers.BandReactionConsumer.as_asgi(),
    ),
]
