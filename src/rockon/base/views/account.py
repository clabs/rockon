from __future__ import annotations

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse


@login_required
def account(request):
    """A view that returns the user profile for logged in users."""
    template = loader.get_template("account/account.html")
    extra_context = {"site_title": "Profil"}
    return HttpResponse(template.render(extra_context, request))


def logout(request):
    template = loader.get_template("account/logout.html")
    extra_context = {
        "site_title": "Logout",
    }
    if request.user.is_authenticated:
        django_auth_logout(request)
    return HttpResponse(template.render(extra_context, request))


def login_request(request):
    if request.user.is_authenticated:
        return redirect(reverse("base:account"))
    template = loader.get_template("account/login.html")
    extra_context = {
        "site_title": "Magic Link",
    }
    return HttpResponse(template.render(extra_context, request))


def login_token(request, token):
    """Shows information corresponding to the magic link token."""
    user = authenticate(request, token=token)
    if not user:
        template = loader.get_template("errors/403.html")
        extra_context = {
            "site_title": "Magic Link angefordert",
            "reason": "Der angefrate Schlüssel wurde nicht gefunden...",
        }
        return HttpResponseForbidden(template.render(extra_context, request))
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect(reverse("crm_user_home"))


def account_create(request):
    """A view that returns the account creation form."""
    template = loader.get_template("account/create.html")
    account_context = request.GET.get("ctx", "crew")
    extra_context = {
        "site_title": "Account erstellen",
        "account_context": account_context,
    }
    return HttpResponse(template.render(extra_context, request))


def account_created(request):
    """A view that returns the account creation form."""
    template = loader.get_template("account/created.html")
    extra_context = {"site_title": "Account erstellt"}
    return HttpResponse(template.render(extra_context, request))


def verify_email(request, token):
    """Verify email."""
    template = loader.get_template("account/verify_email.html")
    extra_context = {"site_title": "E-Mail bestätigen", "token": token}
    return HttpResponse(template.render(extra_context, request))