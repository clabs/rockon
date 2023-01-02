from __future__ import annotations

from django.urls import path

# WONTFIX: stop black and isort from messing up the imports
# fmt: off
from .views import (email_confirmed, email_not_confirmed, magic_link,
                    request_magic_link, request_magic_link_submitted,
                    verify_email)

# fmt: on

urlpatterns = [
    path("verify-email/<str:token>/", verify_email, name="crm_verify_email"),
    path(
        "verify-email/<str:token>/success/", email_confirmed, name="crm_email_confirmed"
    ),
    path(
        "verify-email/<str:token>/error/",
        email_not_confirmed,
        name="crm_email_not_confirmed",
    ),
    path("magic-link/<str:token>/", magic_link, name="crm_magic_link"),
    path("request-magic-link/", request_magic_link, name="crm_request_magic_link"),
    path(
        "magic-link-requested/",
        request_magic_link_submitted,
        name="crm_request_magic_link_submitted",
    ),
]
