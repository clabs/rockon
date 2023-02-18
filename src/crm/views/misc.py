from __future__ import annotations

from django.http import HttpResponse
from django.template import loader


def impressum(request):
    template = loader.get_template("crm/impressum.html")
    context = {
        "site_title": "Impressum",
    }
    return HttpResponse(template.render(context, request))

def privacy(request):
    template = loader.get_template("crm/privacy.html")
    context = {
        "site_title": "Privacy Policy",
    }
    return HttpResponse(template.render(context, request))
