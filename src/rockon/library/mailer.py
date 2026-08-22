"""Thin wrapper around django-q2 async_task for sending emails.

All email dispatch goes through `send_mail_async` so that:
- broker (Redis) failures are caught in one place,
- the HTTP response is never blocked by email delivery,
- callers don't need their own try/except boilerplate.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)


def send_mail_async(
    *,
    subject: str,
    message: str,
    recipient_list: list[str],
    html_message: str | None = None,
    from_email: str | None = None,
    fail_silently: bool = False,
    timeout: int | None = None,
) -> None:
    """Enqueue one email **per recipient** via django-q2.

    Each recipient gets their own message so that addresses are not
    leaked to other recipients.  If the broker is unreachable the error
    is logged and swallowed so the calling request can still return a
    timely HTTP response.
    """
    _from = from_email or settings.EMAIL_DEFAULT_FROM

    try:
        from django_q.tasks import async_task

        for recipient in recipient_list:
            kwargs = {
                'subject': subject,
                'message': message,
                'from_email': _from,
                'recipient_list': [recipient],
                'html_message': html_message,
                'fail_silently': fail_silently,
            }
            if timeout is not None:
                kwargs['timeout'] = timeout

            async_task(send_mail, **kwargs)
    except Exception:
        logger.exception(
            'Failed to enqueue email (subject=%r, recipients=%r). '
            'The broker may be unavailable.',
            subject,
            recipient_list,
        )


def get_admin_url(instance) -> str:
    """Return the absolute URL to the Django admin change page for *instance*."""
    meta = instance._meta
    return (
        f'{settings.DOMAIN}'
        f'{reverse(f"admin:{meta.app_label}_{meta.model_name}_change", args=[instance.pk])}'
    )
