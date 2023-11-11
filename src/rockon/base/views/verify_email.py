from __future__ import annotations

from django.http import HttpResponse
from django.template import loader


def verify_email(request, token):
    """Verify email."""
    template = loader.get_template("crm/mail_confirmed.html")
    extra_context = {"site_title": "E-Mail bestätigen", "token": token}
    return HttpResponse(template.render(extra_context, request))
