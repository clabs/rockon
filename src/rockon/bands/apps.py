from __future__ import annotations

from django.apps import AppConfig


class BandsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rockon.bands'
    label = 'rockonbands'
