from __future__ import annotations

from django.urls import path

from .views import qrcode_generator

urlpatterns = [
    path("qrcode-generator/", qrcode_generator, name="tools_qrcode_generator"),
]
