from __future__ import annotations

from django.urls import path

from .views import (
    account,
    account_created,
    login_request,
    login_token,
    logout,
    passkey_login_redirect,
    passkey_prompt,
    select_context,
    switch_event,
    verify_email,
)

app_name = 'base'

urlpatterns = [
    path('', account, name='account'),
    path('created/', account_created, name='account_created'),
    path('context/', select_context, name='select_context'),
    path('login/', login_request, name='login_request'),
    path('passkey-prompt/', passkey_prompt, name='passkey_prompt'),
    path('passkey-login/', passkey_login_redirect, name='passkey_login_redirect'),
    path('login/<token>/', login_token, name='login_token'),
    path('logout/', logout, name='logout'),
    path('verify/<str:token>/', verify_email, name='verify_email'),
    path('switch-event/<slug:event_slug>/', switch_event, name='switch_event'),
]
