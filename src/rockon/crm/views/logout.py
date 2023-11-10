from __future__ import annotations

from django.contrib.auth import logout
from django.http import HttpResponse
from django.template import loader


def logout_page(request):
    template = loader.get_template("registration/logout.html")
    extra_context = {
        "site_title": "Logout",
    }
    if request.user.is_authenticated:
        logout(request)
    return HttpResponse(template.render(extra_context, request))
