from __future__ import annotations

from django.urls import path

from rockon.base.views import home

from .views import ImprintView, PrivacyView, index_view

urlpatterns = [
    path("", index_view, name="rockon_landing_index"),
    path("home/", home, name="crm_user_home"),
    path("impressum/", ImprintView.as_view(), name="rockon_impressum"),
    path("privacy/", PrivacyView.as_view(), name="rockon_privacy"),
]
