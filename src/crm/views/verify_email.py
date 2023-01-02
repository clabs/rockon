from __future__ import annotations

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from crm.models import EmailVerification, Person


def verify_email(request, token):
    """Verify email."""
    try:
        verification = EmailVerification.objects.get(token=token)
        person = Person.objects.get(id=verification.person.id)
        person.email_verified = True
        person.save()
        verification.delete()
        return redirect(email_confirmed, token=token)
    except (EmailVerification.DoesNotExist, Person.DoesNotExist):
        return redirect(email_not_confirmed, token=token)


def email_confirmed(request, token):
    template = loader.get_template("crm/mail_confirmed.html")
    context = {
        "site_title": "E-Mail bestätigt",
        "success": True,
    }
    return HttpResponse(template.render(context))


def email_not_confirmed(request, token):
    template = loader.get_template("crm/mail_confirmed.html")
    context = {
        "site_title": "E-Mail bestätigt",
        "success": False,
    }
    return HttpResponse(template.render(context))
