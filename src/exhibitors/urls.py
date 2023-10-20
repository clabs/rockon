from __future__ import annotations

from django.urls import path

from .views import signup, signup_submitted

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

# FIXME: add handler for call without slug

urlpatterns = [
    path("signup/<slug>/", signup, name="exhibitor_signup"),
    path(
        "signup/<slug>/submitted/",
        signup_submitted,
        name="exhibitor_signup_submitted",
    ),
]
