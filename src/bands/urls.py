from __future__ import annotations

from django.urls import path

# fmt: off
# WONTFIX: stop isort and black from fighting each other
from .views import members, techrider

# fmt: on

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

urlpatterns = [
    path("<slug>/techrider/", techrider, name="bands_techrider"),
    path("<slug>/members/", members, name="bands_members"),
]
