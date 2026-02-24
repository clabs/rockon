from __future__ import annotations

import json
from collections import defaultdict

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, OuterRef, Subquery, Sum
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.utils.safestring import mark_safe

from rockon.bands.models import Band, BandVote, TimeSlot
from rockon.bands.models.band import BidStatus


@login_required
@user_passes_test(lambda u: u.groups.filter(name='booking').exists())
def booking_bid_overview(request, slug):
    # Use subquery annotations to avoid wide GROUP BY from select_related
    votes_qs = BandVote.objects.filter(band=OuterRef('pk'))
    bands = (
        Band.objects.filter(event__slug=slug)
        .select_related('track', 'contact')
        .annotate(
            votes_count=Subquery(
                votes_qs.values('band').annotate(c=Count('id')).values('c')
            ),
            votes_sum=Subquery(
                votes_qs.values('band').annotate(s=Sum('vote')).values('s')
            ),
            votes_avg=Subquery(
                votes_qs.values('band').annotate(a=Avg('vote')).values('a')
            ),
        )
        .order_by('-votes_sum', '-votes_avg', 'track')
    )

    # Use a subquery for band IDs to avoid premature queryset evaluation
    band_ids_qs = Band.objects.filter(event__slug=slug).values('id')
    vote_distributions = (
        BandVote.objects.filter(band_id__in=band_ids_qs)
        .values('band_id', 'vote')
        .annotate(count=Count('id'))
    )

    # Build vote counters lookup
    vote_counters_map = defaultdict(lambda: {i: 0 for i in range(6)})
    for item in vote_distributions:
        vote_counters_map[item['band_id']][item['vote']] = item['count']

    # Build vote URL base
    vote_url_base = reverse('bands:bid_vote', kwargs={'slug': slug})

    # Serialize bands to JSON for Vue
    bands_data = []
    for band in bands:
        counters = dict(sorted(vote_counters_map[band.id].items()))
        bands_data.append(
            {
                'id': str(band.id),
                'guid': band.guid,
                'name': band.name or band.guid,
                'has_name': bool(band.name),
                'votes_avg': round(float(band.votes_avg or 0), 1),
                'votes_sum': int(band.votes_sum or 0),
                'votes_count': int(band.votes_count or 0),
                'counters': counters,
                'bid_status': band.get_bid_status_display(),
                'bid_status_value': band.bid_status,
                'track_name': band.track.name if band.track else '',
                'bid_complete': band.bid_complete,
                'contact_email': band.contact.email if band.contact else '',
                'admin_url': reverse('admin:rockonbands_band_change', args=[band.id]),
                'vote_url': f'{vote_url_base}#/bid/{band.guid}/',
            }
        )

    template = loader.get_template('booking/bid_overview.html')
    status_choices = [{'value': c.value, 'label': c.label} for c in BidStatus]

    extra_context = {
        'site_title': 'Übersicht',
        'bands_json': mark_safe(json.dumps(bands_data, ensure_ascii=False)),
        'status_choices_json': mark_safe(
            json.dumps(status_choices, ensure_ascii=False)
        ),
    }
    return HttpResponse(template.render(extra_context, request))


@login_required
@user_passes_test(lambda u: u.groups.filter(name='booking').exists())
def booking_lineup(request, slug):
    timeslots = (
        TimeSlot.objects.filter(stage__event__slug=slug)
        .select_related('stage', 'day', 'band__track')
        .order_by('day__day', 'start')
    )
    lineup_bands = (
        Band.objects.filter(event__slug=slug, bid_status='lineup')
        .select_related('track')
        .order_by('name')
    )

    timeslots_data = []
    assigned_band_ids = set()
    for ts in timeslots:
        if ts.band_id:
            assigned_band_ids.add(ts.band_id)
        timeslots_data.append(
            {
                'id': str(ts.id),
                'stage_id': str(ts.stage_id),
                'stage_name': ts.stage.name,
                'day': ts.day.day.isoformat(),
                'day_label': ts.day.day.strftime('%a %d.%m.'),
                'start': ts.start.strftime('%H:%M'),
                'end': ts.end.strftime('%H:%M'),
                'band_id': str(ts.band_id) if ts.band_id else None,
                'band_name': ts.band.name if ts.band else None,
                'band_guid': ts.band.guid if ts.band else None,
                'band_genre': ts.band.genre or '' if ts.band else None,
                'band_track': ts.band.track.name if ts.band and ts.band.track else None,
            }
        )

    unassigned_bands = []
    for band in lineup_bands:
        if band.id not in assigned_band_ids:
            unassigned_bands.append(
                {
                    'id': str(band.id),
                    'name': band.name or band.guid,
                    'guid': band.guid,
                    'genre': band.genre or '',
                    'track': band.track.name if band.track else None,
                }
            )

    vote_url_base = reverse('bands:bid_vote', kwargs={'slug': slug})

    template = loader.get_template('booking/lineup.html')
    extra_context = {
        'site_title': 'Lineup',
        'timeslots_json': mark_safe(json.dumps(timeslots_data, ensure_ascii=False)),
        'unassigned_bands_json': mark_safe(
            json.dumps(unassigned_bands, ensure_ascii=False)
        ),
        'vote_url_base': vote_url_base,
    }
    return HttpResponse(template.render(extra_context, request))
