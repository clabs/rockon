from __future__ import annotations

from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse
from django.template import loader

from bands.models import Band, BandMemberPosition
from crew.models import CrewMemberNutrion


def members(request, band_id):
    try:
        band_obj = Band.objects.get(id=band_id)
    except (Band.DoesNotExist, ValidationError):
        raise Http404("Band nicht gefunden...")

    count = band_obj.band_members.count()

    template = loader.get_template("members.html")
    context = {
        "site_title": "Personenmeldung",
        "band": band_obj,
        "slots": 10 - count,
        "nutrion_choices": CrewMemberNutrion,
        "positions": BandMemberPosition,
    }
    return HttpResponse(template.render(context, request))
