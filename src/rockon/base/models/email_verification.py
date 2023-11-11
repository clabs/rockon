from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template import loader
from django.urls import reverse
from django_q.tasks import async_task

from rockon.library.custom_model import CustomModel, models


class EmailVerification(CustomModel):
    """EmailVerification model."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="email_verification"
    )
    token = models.UUIDField(default=uuid4, editable=False)
    new_email = models.EmailField(max_length=1024, null=True, default=None)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["user"]

    @classmethod
    def create_and_send(cls, user: User, new_email: str = None) -> None:
        """Creates a verification link and sends email to the user."""

        email_verifcation = cls.objects.create(user=user, new_email=new_email)
        email_verifcation.save()

        # FIXME: import the scheme, domain and rest of things from Django settings
        # FIXME: use absolute URLs in templates
        # FIXME: create a helper class for mailings with defined textfields to replace.
        template = loader.get_template("mail/confirm_email_address.html")

        extra_context = {
            "name": user.first_name,
            "email_verification_token": email_verifcation.token,
            "subject": f"{settings.EMAIL_SUBJECT_PREFIX} Bitte bestätige deine E-Mail-Adresse",
            "url": f"{settings.DOMAIN}{reverse('base:verify_email', kwargs={'token': email_verifcation.token})}",
        }

        async_task(
            send_mail,
            subject=extra_context["subject"],
            message=f'Hallo {user.first_name},\nbitte bestätige deine E-Mail-Adresse in dem du diesen Link aufrufst:\n{extra_context["url"]}\n\nSolltest du dich nicht bei unserem rockon-System angemeldet haben, kannst du diese Mail einfach ignorieren, wir werden dir keine weiteren Nachrichten senden.\n\nBis dahin, rockon',
            from_email=settings.EMAIL_DEFAULT_FROM,
            recipient_list=[f"{user.email}"],
            html_message=template.render(extra_context),
            fail_silently=False,
        )
