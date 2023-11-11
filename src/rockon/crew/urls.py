from __future__ import annotations

from django.urls import path

from .views import (
    attendance_table,
    crew_chart,
    crew_shirts,
    join_forward,
    join_slug,
    join_submitted,
)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = "crew"

urlpatterns = [
    path("join/", join_forward, name="join"),
    path(
        "join/submitted/",
        join_submitted,
        name="join_submitted",
    ),
    path("join/<slug:slug>/", join_slug, name="join_slug"),
    path("catering/attendance/", attendance_table, name="catering_attendance"),
    path("coord/overview/", crew_chart, name="coord_overview"),
    path("coord/tshirts/", crew_shirts, name="coord_tshirts"),
]
