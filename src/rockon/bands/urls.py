from __future__ import annotations

from django.urls import path

from .views import application_form, application_router, members, techrider

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

urlpatterns = [
    path("<slug>/techrider/", techrider, name="bands_techrider"),
    path("<slug>/members/", members, name="bands_members"),
    path("<slug>/application/", application_router, name="band_application_router"),
    path("<slug>/application/<guid>/", application_form, name="band_application_form"),
]
