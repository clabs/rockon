from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template import loader
from django.urls import reverse
from django_q.tasks import async_task


class EmailVerification(models.Model):
    """EmailVerification model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="email_verification"
    )
    token = models.UUIDField(default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["user"]

    @classmethod
    def create_and_send(cls, user: User) -> None:
        """Creates a verification link and sends email to the user."""

        email_verifcation = cls.objects.create(user=user)
        email_verifcation.save()

        # FIXME: import the scheme, domain and rest of things from Django settings
        # FIXME: use absolute URLs in templates
        # FIXME: create a helper class for mailings with defined textfields to replace.
        template = loader.get_template("mail/confirm_email_address.html")

        context = {
            "name": user.first_name,
            "email_verification_token": email_verifcation.token,
            "domain": settings.DOMAIN,
        }

        async_task(
            send_mail,
            subject="Bitte bestätige deine E-Mail-Adresse",
            message=f'Hallo {user.first_name},\nbitte bestätige deine E-Mail-Adresse in dem du diesen Link aufrufst:\n{context["domain"]}{reverse("crm_verify_email", kwargs={"token": context["email_verification_token"]})}',
            from_email="rockon@example.com",
            recipient_list=[f"{user.email}"],
            html_message=template.render(context),
            fail_silently=False,
        )
