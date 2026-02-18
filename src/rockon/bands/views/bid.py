from __future__ import annotations

import json

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe

from rockon.bands.models import Band, BandMedia, MediaType, Track
from rockon.bands.models.band import BidStatus
from rockon.base.models import Event
from rockon.library.decorators import check_band_application_open
from rockon.library.federal_states import FederalState


def _can_vote_on_bands(user, event: Event) -> tuple[bool, str | None]:
    """Check if user can vote on bands for an event.

    Returns:
        Tuple of (is_allowed, error_message). error_message is None if allowed.
    """
    is_booking = user.groups.filter(name='booking').exists()

    if not is_booking:
        is_confirmed_crew = user.crewmember_set.filter(
            crew__event=event, state__in=['confirmed', 'arrived']
        ).exists()
        if not is_confirmed_crew:
            return False, (
                'Du bist nicht berechtigt, Bandbewertungen abzugeben, '
                'bitte wende dich an die Crewkoordination und lasse dich für die Crew freischalten.'
            )

    if not event.bid_browsing_allowed and not is_booking:
        return False, 'Die Bandbewertung ist für dieses Event nicht aktiv.'

    return True, None


@login_required
def bid_closed(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(
        request,
        'bid_closed.html',
        {
            'site_title': 'Bewerbungsphase geschlossen',
            'event': event,
        },
    )


@check_band_application_open
def bid_router(request, slug):
    if not request.user.is_authenticated:
        return redirect(f'{reverse("base:login_request")}?ctx=bands')

    try:
        band = Band.objects.get(contact=request.user, event__slug=slug)
        return redirect('bands:bid_form', slug=slug, guid=band.guid)
    except Band.DoesNotExist:
        pass

    event = get_object_or_404(Event, slug=slug)
    new_band = Band.objects.create(event=event, contact=request.user)
    return redirect('bands:bid_form', slug=slug, guid=new_band.guid)


@login_required
def bid_form(request, slug, guid):
    """Display band application form for editing."""
    try:
        band = request.user.bands.select_related('event').get(
            guid=guid, event__slug=slug
        )
    except Band.DoesNotExist:
        return render(
            request,
            'errors/403.html',
            {
                'more_info': 'Diese Bandbewerbung gehört nicht zu deinem Account oder existiert nicht.'
            },
            status=403,
        )

    media = BandMedia.objects.filter(band=band)
    media_by_type = {
        media_type[0]: media.filter(media_type=media_type[0])
        for media_type in MediaType.choices
    }

    return render(
        request,
        'bid_form.html',
        {
            'site_title': 'Band Bewerbung',
            'event': band.event,
            'slug': slug,
            'federal_states': FederalState.choices,
            'band': band,
            'media_by_type': media_by_type,
            'tracks': Track.objects.filter(events=band.event),
        },
    )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='crew').exists())
def bid_vote(
    request, bid: str | None = None, track: str | None = None, slug: str | None = None
):
    """Display band voting interface for crew members."""
    event = get_object_or_404(Event, slug=slug)
    is_booking = request.user.groups.filter(name='booking').exists()

    # Check permissions
    can_vote, error_message = _can_vote_on_bands(request.user, event)
    if not can_vote:
        if error_message and 'nicht berechtigt' in error_message:
            raise PermissionDenied(error_message)
        return render(
            request, 'errors/403.html', {'more_info': error_message}, status=403
        )

    # Prepare data for JavaScript - convert UUIDs to strings for JSON serialization
    tracks = [
        {'id': str(t['id']), 'name': t['name'], 'slug': t['slug']}
        for t in Track.objects.filter(events=event).values('id', 'name', 'slug')
    ]
    user_votes = [
        {'band__id': str(v['band__id']), 'vote': v['vote']}
        for v in request.user.band_votes.filter(event=event).values('band__id', 'vote')
    ]

    return render(
        request,
        'bid_vote.html',
        {
            'media_url': settings.MEDIA_URL,
            'site_title': 'Bandbewertung',
            'tracks': mark_safe(json.dumps(tracks)),
            'federal_states': mark_safe(json.dumps(list(FederalState.choices))),
            'bid_states': mark_safe(json.dumps(list(BidStatus.choices))),
            'trackid': mark_safe(json.dumps(track)),
            'bandid': mark_safe(json.dumps(bid)),
            'user_votes': mark_safe(json.dumps(user_votes)),
            'allow_changes': mark_safe(json.dumps(is_booking)),
            'allow_votes': mark_safe(json.dumps(event.bid_vote_allowed)),
        },
    )
