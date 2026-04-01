from __future__ import annotations

from django.conf import settings


def get_build_date(_request):
    return {'APP_BUILD_DATE': settings.APP_BUILD_DATE}


def get_build_hash(_request):
    return {'APP_BUILD_HASH': settings.APP_BUILD_HASH}
