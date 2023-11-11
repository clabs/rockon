from __future__ import annotations

from django.urls import path

from .views import (
    account,
    account_create,
    account_created,
    login_request,
    login_token,
    logout,
    verify_email,
)

app_name = "base"

urlpatterns = [
    path("", account, name="account"),
    path("account/created/", account_created, name="account_created"),
    path("create/", account_create, name="account_create"),
    path("login/", login_request, name="login_request"),
    path("login/<token>/", login_token, name="login_token"),
    path("logout/", logout, name="logout"),
    path("verify/<str:token>/", verify_email, name="verify_email"),
]