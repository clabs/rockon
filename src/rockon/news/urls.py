from __future__ import annotations

from django.urls import path

from .views import editor_home

app_name = 'news'

urlpatterns = [
    path('editor/', editor_home, name='editor'),
]
