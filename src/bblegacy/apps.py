from __future__ import annotations

from django.apps import AppConfig


class BbLegacyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bblegacy"
