from __future__ import annotations

from django.urls import path

from .views import (
    get_account_create,
    get_account_created,
    get_user_homeview,
    get_user_profile,
    logout_page,
    magic_link,
    request_magic_link,
    verify_email,
)

urlpatterns = [
    path(
        "account/create/<str:account_context>/",
        get_account_create,
        name="crm_account_create",
    ),
    path("account/created/", get_account_created, name="crm_account_created"),
    path("verify-email/<str:token>/", verify_email, name="crm_verify_email"),
    path("magic-link/<str:token>/", magic_link, name="crm_magic_link"),
    path("request-magic-link/", request_magic_link, name="crm_request_magic_link"),
    path("home/", get_user_homeview, name="crm_user_home"),
    path("me/profile/", get_user_profile, name="crm_user_profile"),
    path("logout/", logout_page, name="crm_logout"),
]
