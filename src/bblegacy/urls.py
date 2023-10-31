from __future__ import annotations

from django.urls import path

from .views import (
    auth_local,
    bid_handler,
    event_handler,
    get_region,
    media_handler,
    new_media_handler,
    region_list,
    track_handler,
    user_handler,
)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

urlpatterns = [
    path("auth/local/", auth_local, name="bblegacy_auth_local"),
    path("bids/", bid_handler, name="bblegacy_bids"),
    path("bids/<str:bid_id>/", bid_handler, name="bblegacy_bids"),
    path("events/", event_handler, name="bblegacy_events"),
    path("events/<str:event_id>/", event_handler, name="bblegacy_modify_event"),
    path("media/", new_media_handler, name="bblegacy_new_media"),
    path("media/<str:media_id>/", media_handler, name="bblegacy_media_handler"),
    path("regions/", region_list, name="bblegacy_regions"),
    path("regions/<str:region_id>/", get_region, name="bblegacy_get_region"),
    path("tracks/", track_handler, name="bblegacy_track_handler"),
    path("tracks/<str:track_id>/", track_handler, name="bblegacy_delete_track"),
    path("users/", user_handler, name="bblegacy_get_users"),
    path("users/<str:user_id>/", user_handler, name="bblegacy_get_user"),
]
