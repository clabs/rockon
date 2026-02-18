from __future__ import annotations

from collections import defaultdict

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Sum
from django.http import HttpResponse
from django.template import loader

from rockon.bands.models import Band, BandVote


@login_required
@user_passes_test(lambda u: u.groups.filter(name='booking').exists())
def booking_bid_overview(request, slug):
    bands = (
        Band.objects.filter(event__slug=slug)
        .select_related('track', 'contact')
        .annotate(
            votes_count=Count('votes'),
            votes_sum=Sum('votes__vote'),
            votes_avg=Avg('votes__vote'),
        )
        .order_by('-votes_sum', '-votes_avg', 'track')
    )

    # Fetch all vote distributions in a single query
    band_ids = [band.id for band in bands]
    vote_distributions = (
        BandVote.objects.filter(band_id__in=band_ids)
        .values('band_id', 'vote')
        .annotate(count=Count('id'))
    )

    # Build vote counters lookup
    vote_counters_map = defaultdict(lambda: {i: 0 for i in range(6)})
    for item in vote_distributions:
        vote_counters_map[item['band_id']][item['vote']] = item['count']

    # Attach counters to bands
    for band in bands:
        setattr(band, 'counters', dict(sorted(vote_counters_map[band.id].items())))

    template = loader.get_template('booking/bid_overview.html')
    extra_context = {
        'site_title': 'Übersicht',
        'bands': bands,
    }
    return HttpResponse(template.render(extra_context, request))
