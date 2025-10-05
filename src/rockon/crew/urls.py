from __future__ import annotations

from django.urls import path

from .views import (
    attendance_table,
    crew_chart,
    crew_shirts,
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
    path('coord/tshirts/', crew_shirts, name='coord_tshirts'),
]
