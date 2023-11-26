from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.template import loader

from rockon.bands.models import Band, BandMedia, MediaType
from rockon.base.models import Event
from rockon.library.decorators import check_band_application_open
from rockon.library.federal_states import FederalState


@check_band_application_open
def bid_root(request):
    if getattr(request.user, "band", None):
        return redirect(
            "bands:bid_form",
            slug=request.user.band.event.slug,
            guid=request.user.band.guid,
        )
    event = Event.objects.filter(is_current=True).first()
    return redirect("bands:bid_preselect", slug=event.slug)


@check_band_application_open
def bid_preselect(request, slug):
    if request.user.is_authenticated:
        return redirect("bands:bid_router", slug=slug)
    template = loader.get_template("bid_preselect.html")
    extra_context = {"site_title": "Vorauswahl", "slug": slug}
    return HttpResponse(template.render(extra_context, request))


def bid_closed(request, slug):
    template = loader.get_template("bid_closed.html")
    event = Event.objects.get(slug=slug)
    extra_context = {"site_title": "Bewerbungsphase geschlossen", "event": event}
    return HttpResponse(template.render(extra_context, request))


@login_required
def bid_router(request, slug):
    if hasattr(request.user, "band"):
        band = request.user.band
        return redirect("bands:bid_form", slug=slug, guid=band.guid)
    event = get_object_or_404(Event, slug=slug)
    if not event.band_application_open:
        return redirect("bands:bid_closed", slug=slug)

    new_band = Band.objects.create(
        event=Event.objects.get(slug=slug), contact=request.user
    )
    new_band.save()

    return redirect("bands:bid_form", slug=slug, guid=new_band.guid)


@login_required
def bid_form(request, slug, guid):
    if not request.user.band.guid == guid:
        template = loader.get_template("errors/403.html")
        return HttpResponseForbidden(
            template.render(
                {"more_info": "Diese Bandbewerbung gehört nicht zu deinem Account."},
                request,
            )
        )
    template = loader.get_template("bid_form.html")
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
