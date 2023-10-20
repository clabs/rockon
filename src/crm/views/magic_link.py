from __future__ import annotations

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse


def request_magic_link(request):
    if request.user.is_authenticated:
        return redirect(reverse("crm_user_profile"))
    template = loader.get_template("magic_link.html")
    extra_context = {
        "site_title": "Magic Link",
    }
    return HttpResponse(template.render(extra_context, request))


def magic_link(request, token):
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
    # if not user:
    #     raise PermissionDenied
    # return HttpResponseForbidden("Der angefrate Schlüssel wurde nicht gefunden...")
    return redirect(reverse("crm_user_profile"))
