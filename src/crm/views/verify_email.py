from __future__ import annotations

from django.http import Http404, HttpResponse
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
        template = loader.get_template("crm/mail_confirmed.html")
        context = {"site_title": "E-Mail bestätigt"}
        return HttpResponse(template.render(context))
    except (EmailVerification.DoesNotExist, Person.DoesNotExist):
        raise Http404("Der angefrate Schlüssel wurde nicht gefunden...")
