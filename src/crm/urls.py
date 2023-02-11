from __future__ import annotations

from django.urls import path

# WONTFIX: stop black and isort from messing up the imports
# fmt: off
from .views import (
    get_user_profile,
    logout_page,
    magic_link,
    request_magic_link,
    request_magic_link_submitted,
    verify_email,
)

# fmt: on

urlpatterns = [
    path("verify-email/<str:token>/", verify_email, name="crm_verify_email"),
    path("magic-link/<str:token>/", magic_link, name="crm_magic_link"),
    path("request-magic-link/", request_magic_link, name="crm_request_magic_link"),
    path(
        "magic-link-requested/",
        request_magic_link_submitted,
        name="crm_request_magic_link_submitted",
    ),
    path("me/", get_user_profile, name="crm_user_profile"),
    path("logout/", logout_page, name="crm_logout"),
]
