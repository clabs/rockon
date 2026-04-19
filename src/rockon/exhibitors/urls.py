from __future__ import annotations

from django.urls import path

from .views import exhibitor_assets, exhibitor_list, join

# Caching:
# path("chat/list/", cache_page(60*15)(ChatList.as_view()), name="chat_list"),

app_name = 'exhibitors'

urlpatterns = [
    path('join/', join, name='join'),
    path('list/', exhibitor_list, name='exhibitor_list'),
    path('assets/', exhibitor_assets, name='exhibitor_assets'),
]
