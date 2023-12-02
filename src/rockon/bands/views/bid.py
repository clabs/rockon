from __future__ import annotations

import json
from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
from django.utils.safestring import mark_safe

from rockon.bands.models import Band, BandMedia, MediaType, Track
from rockon.base.models import Event
from rockon.library.decorators import check_band_application_open
from rockon.library.federal_states import FederalState


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Event):
            return obj.id
        return super().default(obj)


@login_required
@check_band_application_open
def bid_root(request):
    if getattr(request.user, "band", None):
        return redirect(
            "bands:bid_form",
            slug=request.user.band.event.slug,
            guid=request.user.band.guid,
        )
    event = Event.objects.get(id=request.session["current_event"])
    return redirect("bands:bid_router", slug=event.slug)


@login_required
def bid_closed(request, slug):
    template = loader.get_template("bid_closed.html")
    event = Event.objects.get(slug=slug)
    extra_context = {"site_title": "Bewerbungsphase geschlossen", "event": event}
    return HttpResponse(template.render(extra_context, request))


@check_band_application_open
def bid_router(request, slug):
    if not request.user.is_authenticated:
        url = reverse("base:login_request")
        url += f"?ctx=bands"
        return redirect(url)
    # Checks if user profile is complete
    # if not request.user.profile.is_profile_complete_band():
    #     event = Event.objects.get(slug=slug)
    #     template = loader.get_template("bid_profile_incomplete.html")
    #     extra_context = {
    #         "site_title": "Profil unvollständig - Bandbewerbung",
    #         "event": event,
    #         "slug": slug,
    #     }
    #     return HttpResponse(template.render(extra_context, request))
    if hasattr(request.user, "band"):
        band = request.user.band
        return redirect("bands:bid_form", slug=slug, guid=band.guid)

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


@login_required
def bid_vote(request, bid: str = None, track: str = None):
    template = loader.get_template("bid_vote.html")
    bands = Band.objects.filter(event__id=request.session["current_event"])
    bands_json = mark_safe(json.dumps(list(bands.values()), cls=CustomJSONEncoder))
    tracks = Track.objects.filter(events__id=request.session["current_event"])
    tracks_json = mark_safe(json.dumps(list(tracks.values()), cls=CustomJSONEncoder))
    track_slug_json = mark_safe(json.dumps(track, cls=CustomJSONEncoder))
    band_guid_json = mark_safe(json.dumps(bid, cls=CustomJSONEncoder))
    extra_context = {
        "site_title": "Band Bewertung",
        "bands": bands_json,
        "tracks": tracks_json,
        "trackid": track_slug_json,
        "bandid": band_guid_json,
    }
    return HttpResponse(template.render(extra_context, request))
