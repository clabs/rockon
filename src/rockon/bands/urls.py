from __future__ import annotations

from django.urls import path, re_path

from .views import (
    bid_closed,
    bid_form,
    bid_root,
    bid_router,
    bid_vote,
    members,
    techrider,
)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = "bands"

urlpatterns = [
    path("vote/", bid_vote, name="bid_vote"),
    re_path(
        r"^vote/(?P<track_slug>[a-zA-Z0-9_-]+)/$",
        bid_vote,
        name="bid_vote_with_trackid",
    ),
    re_path(
        r"^vote/(?P<track_slug>[a-zA-Z0-9_-]+)/(?P<band_guid>[a-zA-Z0-9_-]+)/$",
        bid_vote,
        name="bid_vote_with_params",
    ),
    path("bid/", bid_root, name="bid_root"),
    path("bid/<slug>/", bid_router, name="bid_router"),
    path("bid/<slug>/closed/", bid_closed, name="bid_closed"),
    path("bid/<slug>/<guid>/", bid_form, name="bid_form"),
    # path("<slug>/techrider/", techrider, name="bands_techrider"),
    # path("<slug>/members/", members, name="bands_members"),
]
