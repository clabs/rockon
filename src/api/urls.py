from __future__ import annotations

from django.urls import path

from api.views import (
    bandmember_signup,
    crew_signup,
    exhibitor_signup,
    request_magic_link,
    verify_email,
)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

urlpatterns = [
    path("crm/crew/<slug:slug>/signup/", crew_signup, name="api_crew_signup"),
    path(
        "crm/exhibitor/<slug:slug>/signup/",
        exhibitor_signup,
        name="api_exhibitor_signup",
    ),
    path("crm/verify-email/", verify_email, name="api_crm_verify_email"),
    path(
        "crm/request-magic-link/", request_magic_link, name="api_crm_request_magic_link"
    ),
    path("bands/bandmember/", bandmember_signup, name="api_bandmember_signup"),
]
