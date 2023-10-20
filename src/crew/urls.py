from __future__ import annotations

from django.urls import path

from .views import (
    PreselectView,
    SignupSubmittedView,
    attendance_table,
    crew_chart,
    crew_shirts,
    signup,
    signup_root,
)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

# FIXME: add handler for call without slug

urlpatterns = [
    path("signup/<slug:slug>/", signup_root, name="crew_root"),
    # path("signup/<slug:slug>/preselect/", preselect, name="crew_preselect"),
    path(
        "signup/<slug:slug>/preselect/", PreselectView.as_view(), name="crew_preselect"
    ),
    path("signup/<slug:slug>/form/", signup, name="crew_signup"),
    path(
        "signup/<slug:slug>/submitted/",
        SignupSubmittedView.as_view(),
        name="crew_signup_submitted",
    ),
    path("kitchen/attendance/", attendance_table, name="kitchen_attendance"),
    path("crewcoord/overview/", crew_chart, name="crewcoord_overview"),
    path("crewcoord/tshirts/", crew_shirts, name="crewcoord_tshirts"),
]
