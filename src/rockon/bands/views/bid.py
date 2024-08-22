from __future__ import annotations

import json
from uuid import UUID

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
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
        # we need @property fields in the JSON
        if hasattr(obj, "__dict__"):
            data = obj.__dict__
            # Add properties here
            data.update(
                {
                    prop: getattr(obj, prop)
                    for prop in dir(obj)
                    if isinstance(getattr(obj, prop), property)
                    and not prop.startswith("__")
                }
            )
            return data
        return super().default(obj)


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
@user_passes_test(lambda u: u.groups.filter(name="crew").exists())
def bid_vote(request, bid: str = None, track: str = None, slug: str = None):
    if not request.user.crewmember_set.filter(
        crew__event__slug=slug, state="confirmed"
    ).exists():
        raise PermissionDenied(
            "Du bist nicht berechtigt, Bandbewertungen abzugeben, bitte wende dich an die Crewkoordination und lasse dich für die Crew freischalten."
        )
    if (
        not Event.objects.get(slug=slug).bid_vote_allowed
        and not request.user.groups.filter(name="booking").exists()
    ):
        template = loader.get_template("errors/403.html")
        return HttpResponseForbidden(
            template.render(
                {"more_info": "Die Bandbewertung ist für dieses Event nicht aktiv."},
                request,
            )
        )
    template = loader.get_template("bid_vote.html")
    tracks = Track.objects.filter(events__slug=slug)
    tracks_json = mark_safe(json.dumps(list(tracks.values()), cls=CustomJSONEncoder))
    federal_states = FederalState.choices
    federal_states_json = mark_safe(json.dumps(federal_states))
    track_slug_json = mark_safe(json.dumps(track, cls=CustomJSONEncoder))
    band_guid_json = mark_safe(json.dumps(bid, cls=CustomJSONEncoder))
    allow_changes = mark_safe(
        json.dumps(request.user.groups.filter(name="booking").exists())
    )
    media_url = settings.MEDIA_URL
    user_votes = request.user.band_votes.filter(event__slug=slug).values(
        "band__id", "vote"
    )
    user_votes_json = mark_safe(json.dumps(list(user_votes), cls=CustomJSONEncoder))
    extra_context = {
        "media_url": media_url,
        "site_title": "Band Bewertung",
        "tracks": tracks_json,
        "federal_states": federal_states_json,
        "trackid": track_slug_json,
        "bandid": band_guid_json,
        "user_votes": user_votes_json,
        "allow_changes": allow_changes,
    }
    return HttpResponse(template.render(extra_context, request))
