from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template import loader

from bands.models import Band, BandMedia, MediaType
from event.models import Event
from library.federal_states import FederalState


@login_required
def application_router(request, slug):
    if hasattr(request.user, "band"):
        band = request.user.band
        return redirect("band_application_form", slug=slug, guid=band.guid)
    new_band = Band.objects.create(
        event=Event.objects.get(slug=slug), contact=request.user
    )
    new_band.save()

    return redirect("band_application_form", slug=slug, guid=new_band.guid)


@login_required
def application_form(request, slug, guid):
    if not request.user.band.guid == guid:
        template = loader.get_template("errors/403.html")
        return HttpResponseForbidden(
            template.render(
                {"more_info": "Diese Bandbewerbung gehört nicht zu deinem Account."},
                request,
            )
        )
    template = loader.get_template("application_form.html")
    event = Event.objects.get(slug=slug)
    media = BandMedia.objects.filter(band=request.user.band)
    media_by_type = {}
    for media_type in MediaType.choices:
        media_by_type[media_type[0]] = media.filter(media_type=media_type[0])
    extra_context = {
        "site_title": "Band Bewerbung",
        "event": event,
        "slug": slug,
        "federal_states": FederalState.choices,
        "band": Band.objects.get(guid=guid),
        "media_by_type": media_by_type,
    }
    return HttpResponse(template.render(extra_context, request))
