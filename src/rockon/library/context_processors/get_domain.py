from __future__ import annotations

from django.conf import settings


def get_domain(request):
    return {"DOMAIN": settings.DOMAIN}
