from __future__ import annotations

from django.urls import path

from .views import streaming_upload

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

urlpatterns = [
    path('<band>/<filename>', streaming_upload, name='bands_streaming_upload'),
]
