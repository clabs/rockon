from __future__ import annotations

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotFound
from django.template import loader

from crm.models import EmailVerification


def verify_email(request, token):
    """Verify email."""
    try:
        verification = EmailVerification.objects.get(token=token)
        user = User.objects.get(id=verification.user.id)
        user.email_verified = True
        user.save()
        verification.delete()
        template = loader.get_template("crm/mail_confirmed.html")
        context = {"site_title": "E-Mail bestätigt"}
        return HttpResponse(template.render(context))
    except (EmailVerification.DoesNotExist, User.DoesNotExist):
        raise HttpResponseNotFound("Der angefrate Schlüssel wurde nicht gefunden...")
