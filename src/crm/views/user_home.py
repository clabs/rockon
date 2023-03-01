from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader


@login_required
def get_user_homeview(request):
    """A view that returns the user homeview for logged in users."""
    template = loader.get_template("crm/user_home.html")
    context = {"site_title": "Profil"}
    return HttpResponse(template.render(context, request))
