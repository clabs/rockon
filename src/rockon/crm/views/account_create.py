from __future__ import annotations

from django.http import HttpResponse
from django.template import loader


def get_account_create(request, account_context: str):
    """A view that returns the account creation form."""
    template = loader.get_template("account_create.html")
    extra_context = {
        "site_title": "Account erstellen",
        "account_context": account_context,
    }
    return HttpResponse(template.render(extra_context, request))


def get_account_created(request):
    """A view that returns the account creation form."""
    template = loader.get_template("account_created.html")
    extra_context = {"site_title": "Account erstellt"}
    return HttpResponse(template.render(extra_context, request))
