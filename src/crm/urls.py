from __future__ import annotations

from .views import verify_email, magic_link, request_magic_link, request_magic_link_submitted

from django.urls import path

urlpatterns = [
    path("verify-email/<str:token>", verify_email, name="crm_verify_email"),
    path("magic-link/<str:token>", magic_link, name="crm_magic_link"),
    path("request-magic-link", request_magic_link, name="crm_request_magic_link"),
    path("magic-link-requested", request_magic_link_submitted, name="crm_request_magic_link_submitted"),
]
