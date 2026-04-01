from __future__ import annotations

from django.conf import settings


def get_domain(_request):
    return {'DOMAIN': settings.DOMAIN}
