from __future__ import annotations

from django.urls import path, re_path

from .views import (
    bid_closed,
    bid_form,
    bid_router,
    bid_vote,
    booking_bid_overview,
    members,
    techrider,
)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = "bands"

urlpatterns = [
    path("vote/", bid_vote, name="bid_vote"),
    path(
        "vote/bid/",
        bid_vote,
        name="bid_vote_with_trackid",
    ),
    path("vote/track/<slug:track>/", bid_vote, name="bid_vote_with_params"),
    path("bid/", bid_router, name="bid_router"),
    path("bid/closed/", bid_closed, name="bid_closed"),
    path("bid/<guid>/", bid_form, name="bid_form"),
    path("booking/bid_overview/", booking_bid_overview, name="booking_bid_overview"),
    # path("techrider/", techrider, name="bands_techrider"),
    path("<slug_guid>/members/", members, name="bands_members"),
]
