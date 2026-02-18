from __future__ import annotations

from django.urls import path

from .views import join

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = 'exhibitors'

urlpatterns = [
    path('join/', join, name='join'),
]
