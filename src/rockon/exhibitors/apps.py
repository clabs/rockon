from __future__ import annotations

from django.apps import AppConfig


class ExhibitorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rockon.exhibitors'
    label = 'rockonexhibitors'
