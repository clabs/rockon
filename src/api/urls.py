from __future__ import annotations

from django.urls import path

from api.views import request_magic_link, signup

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

urlpatterns = [
    path("crm/<slug:slug>/signup/", signup, name="api_signup"),
    path("crm/request-magic-link/", request_magic_link, name="api_request_magic_link"),
]
