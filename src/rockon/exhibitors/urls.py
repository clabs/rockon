from __future__ import annotations

from django.urls import path

from .views import join, signup_submitted

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = 'exhibitors'

urlpatterns = [
    path(
        'join/submitted/',
        signup_submitted,
        name='join_submitted',
    ),
    path('join/', join, name='join'),
]
