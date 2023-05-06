from __future__ import annotations

from django.http import HttpResponse
from django.template import loader


def qrcode_generator(request):
    template = loader.get_template("qrcode_generator.html")
    extra_context = {"site_title": "QR"}
    return HttpResponse(template.render(extra_context, request))
