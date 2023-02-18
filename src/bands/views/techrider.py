from __future__ import annotations

from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse
from django.template import loader

from bands.models import Band


def techrider(request, band_id):
    try:
        band_obj = Band.objects.get(id=band_id)
    except (Band.DoesNotExist, ValidationError):
        raise Http404("Band nicht gefunden...")

    template = loader.get_template("bands/techrider.html")
    context = {
        "site_title": "Techrider",
        "band": band_obj,
    }
    return HttpResponse(template.render(context, request))
