from __future__ import annotations

from django.urls import path

from .views import display_qr_code, link_shortener

urlpatterns = [
    path("<str:slug>/", link_shortener, name="tools_link_shortener"),
    path("<str:slug>/qr/", display_qr_code, name="tools_link_shortener_qr"),
]
