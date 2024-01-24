from __future__ import annotations

from django.urls import path

from .views import join_forward, join_slug, signup, signup_submitted

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = "exhibitors"

urlpatterns = [
    path("join/", join_forward, name="join"),
    path(
        "join/submitted/",
        signup_submitted,
        name="join_submitted",
    ),
    path("join/<slug:slug>/", join_slug, name="join_slug"),
]
