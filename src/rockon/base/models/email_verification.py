from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.template import loader
from django.urls import reverse

from rockon.library.custom_model import CustomModel, models
from rockon.library.mailer import send_mail_async


class EmailVerification(CustomModel):
    """EmailVerification model."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='email_verification'
    )
    token = models.UUIDField(default=uuid4, editable=False)
    new_email = models.EmailField(max_length=1024, null=True, default=None, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['user']

    @classmethod
    def create_and_send(cls, user: User, new_email: str = None) -> None:
        """Creates a verification link and sends email to the user."""

        email_verifcation = cls.objects.create(user=user, new_email=new_email)
        email_verifcation.save()

        # FIXME: import the scheme, domain and rest of things from Django settings
        # FIXME: use absolute URLs in templates
        # FIXME: create a helper class for mailings with defined textfields to replace.
        template = loader.get_template('mail/confirm_email_address.html')

        extra_context = {
            'name': user.first_name,
            'email_verification_token': email_verifcation.token,
            'subject': f'{settings.EMAIL_SUBJECT_PREFIX} Bitte bestätige deine E-Mail-Adresse',
            'url': f'{settings.DOMAIN}{reverse("base:verify_email", kwargs={"token": email_verifcation.token})}',
        }

        send_mail_async(
            subject=extra_context['subject'],
            message=f'Hallo {user.first_name},\nbitte bestätige deine E-Mail-Adresse in dem du diesen Link aufrufst:\n{extra_context["url"]}\n\nSolltest du dich nicht bei unserem rockon-System angemeldet haben, kannst du diese Mail einfach ignorieren, wir werden dir keine weiteren Nachrichten senden.\n\nBis dahin, rockon',
            recipient_list=[f'{user.email}'],
            html_message=template.render(extra_context),
        )
