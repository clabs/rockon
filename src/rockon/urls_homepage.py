from __future__ import annotations

from django.urls import path

from .views import ImprintView, IndexView, PrivacyView

urlpatterns = [
    path("", IndexView.as_view(), name="rockon_landing_index"),
    path("impressum/", ImprintView.as_view(), name="rockon_impressum"),
    path("privacy/", PrivacyView.as_view(), name="rockon_privacy"),
]
