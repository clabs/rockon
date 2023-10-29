from __future__ import annotations

from django.urls import path

from .views import serve_media

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

urlpatterns = [
    path("", serve_media, name="bblegacy_serve_media"),
]
