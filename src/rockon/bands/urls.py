from __future__ import annotations

from django.urls import path, re_path

from .views import (
    bid_closed,
    bid_form,
    bid_root,
    bid_router,
    bid_vote,
    booking_bide_overview,
    members,
    techrider,
)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = "bands"

urlpatterns = [
    path("vote/", bid_vote, name="bid_vote"),
    re_path(
        r"^vote/bid/(?P<bid>[a-zA-Z0-9_-]+)/$",
        bid_vote,
        name="bid_vote_with_trackid",
    ),
    path("vote/track/<slug:track>/", bid_vote, name="bid_vote_with_params"),
    path("bid/", bid_root, name="bid_root"),
    path("bid/<slug>/", bid_router, name="bid_router"),
    path("bid/<slug>/closed/", bid_closed, name="bid_closed"),
    path("bid/<slug>/<guid>/", bid_form, name="bid_form"),
    path("booking/bid_overview/", booking_bide_overview, name="booking_bid_overview"),
    # path("<slug>/techrider/", techrider, name="bands_techrider"),
    path("<slug>/members/", members, name="bands_members"),
]
