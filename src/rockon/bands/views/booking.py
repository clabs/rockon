from __future__ import annotations

from collections import Counter, defaultdict

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Sum
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from rockon.bands.models import Band


@login_required
@user_passes_test(lambda u: u.groups.filter(name="booking").exists())
@cache_page(60 * 5)
@vary_on_cookie
def booking_bid_overview(request, slug):
    bands = (
        Band.objects.filter(event__slug=slug)
        .annotate(
            votes_count=Count("votes"),
            votes_sum=Sum("votes__vote"),
            votes_avg=Avg("votes__vote"),
            vote_counters=Count("votes__vote", distinct=True),
        )
        .order_by("-votes_sum", "-votes_avg", "track")
    )
    for index, band in enumerate(bands):
        counters = defaultdict(int, Counter(band.votes.values_list("vote", flat=True)))
        if not counters:
            continue
        for i in range(6):
            counters[i]
        counters = dict(sorted(counters.items()))
        setattr(bands[index], "counters", dict(counters))

    template = loader.get_template("booking/bid_overview.html")
    extra_context = {
        "site_title": "Bandbewertungen",
        "bands": bands,
    }
    return HttpResponse(template.render(extra_context, request))
