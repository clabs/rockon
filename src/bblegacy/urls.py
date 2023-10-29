from __future__ import annotations

from django.urls import path

from .views import (
    bid_create,
    bid_handler,
    event_list,
    get_region,
    media_handler,
    new_media_handler,
    region_list,
)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

urlpatterns = [
    path("events/", event_list, name="bblegacy_events"),
    path("regions/", region_list, name="bblegacy_regions"),
    path("regions/<str:region_id>/", get_region, name="bblegacy_get_region"),
    path("bids/", bid_create, name="bblegacy_bids"),
    path("bids/<str:id>/", bid_handler, name="bblegacy_bids_obj"),
    path("media/", new_media_handler, name="bblegacy_new_media"),
    path("media/<str:media_id>/", media_handler, name="bblegacy_media_handler"),
]
