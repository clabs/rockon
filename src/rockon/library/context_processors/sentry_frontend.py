from __future__ import annotations

from django.conf import settings


def get_sentry_data(request):
    return {
        "SENTRY_FRONTEND_ENABLED": settings.SENTRY_FRONTEND_ENABLED,
        "SENTRY_DSN": settings.SENTRY_DSN,
        "SENTRY_ENVIRONMENT": settings.SENTRY_ENVIRONMENT,
        "SENTRY_TRACES_SAMPLE_RATE": settings.SENTRY_TRACES_SAMPLE_RATE,
        "SENTRY_SEND_DEFAULT_PII": settings.SENTRY_SEND_DEFAULT_PII,
    }
