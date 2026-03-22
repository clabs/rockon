from __future__ import annotations

from django.urls import path

from .views import (
    attendance_table,
    crew_availability_matrix,
    crew_chart,
    crew_member_management,
    crew_shirts,
    crew_team_management,
    guestlist_entries,
    join,
    join_submitted,
)

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = 'crew'

urlpatterns = [
    path(
        'join/submitted/',
        join_submitted,
        name='join_submitted',
    ),
    path('join/', join, name='join'),
    path('guestlist/', guestlist_entries, name='guestlist_entries'),
    path('catering/attendance/', attendance_table, name='catering_attendance'),
    path('coord/overview/', crew_chart, name='coord_overview'),
    path('coord/availability/', crew_availability_matrix, name='coord_availability'),
    path('coord/members/', crew_member_management, name='coord_members'),
    path('coord/tshirts/', crew_shirts, name='coord_tshirts'),
    path('coord/teams/', crew_team_management, name='coord_teams'),
]
