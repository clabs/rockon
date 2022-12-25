from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.decorators.cache import cache_page

# fmt: off
# FIXME stop isort and black from fighting each other
from .views import signup, preselect, signup_submitted, signup_root

# fmt: on

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

# FIXME: add handler for call without slug

urlpatterns = [
    path("signup/<slug:slug>", signup_root, name="crew_root"),
    path("signup/<slug:slug>/preselect", preselect, name="crew_preselect"),
    path("signup/<slug:slug>/signup", signup, name="crew_signup"),
    path("signup/<slug:slug>/submitted", signup_submitted, name="crew_signup_submitted"),
]
