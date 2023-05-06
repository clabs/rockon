from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template import loader
from django.urls import reverse
from django.utils.timezone import make_aware
from django_q.tasks import async_task


class MagicLink(models.Model):
    """MagicLink model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="magic_links")
    token = models.UUIDField(default=uuid4, editable=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["user", "expires_at"]

    @classmethod
    def create_and_send(cls, user: User, expires_at: datetime) -> None:
        # FIXME: this should be a setting
        # MagicLink.objects.filter(user=user).delete()

        _expires_at = make_aware(datetime.now() + timedelta(weeks=4))

        # FIXME: this should be a setting
        # FIXME: improve timedelta handling
        magic_link = MagicLink.objects.create(user=user, expires_at=_expires_at)
        magic_link.save()

        # FIXME: import the scheme, domain and rest of things from Django settings
        # FIXME: use absolute URLs in templates
        # FIXME: create a helper class for mailings with defined textfields to replace.
        template = loader.get_template("mail/magic_link.html")
        extra_context = {
            "name": user.first_name,
            "magic_link_token": magic_link.token,
            "expires_at": _expires_at,
            "expires_at_format": _expires_at.strftime("%d.%m.%Y - %H:%M"),
            "domain": settings.DOMAIN,
            "recipient": f"{user.email}",
            "subject": f"{settings.EMAIL_SUBJECT_PREFIX} Dein Magic Link",
            "magic_link": f'{settings.DOMAIN}{reverse("crm_magic_link", kwargs={"token": magic_link.token})}',
        }

        message = f'Hallo {extra_context["name"]},\nhier findest du deinen persönlichen Link \
                    zum einsehen und ändern deiner persönlichen Daten:\n{extra_context["magic_link"]}'

        async_task(
            send_mail,
            subject=extra_context["subject"],
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[extra_context["recipient"]],
            html_message=template.render(extra_context),
            fail_silently=False,
        )
