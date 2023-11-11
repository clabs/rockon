from __future__ import annotations

from django.urls import path

from .views import bid_form, bid_preselect, bid_root, bid_router, members, techrider

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = "bands"

urlpatterns = [
    path("bid/", bid_root, name="bid_root"),
    path("bid/<slug>/", bid_preselect, name="bid_preselect"),
    path("bid/<slug>/new/", bid_router, name="bid_router"),
    path("bid/<slug>/<guid>/", bid_form, name="bid_form"),
    # path("<slug>/techrider/", techrider, name="bands_techrider"),
    # path("<slug>/members/", members, name="bands_members"),
    # path("<slug>/application/", application_router, name="band_application_router"),
    # path("<slug>/application/<guid>/", application_form, name="band_application_form"),
]
