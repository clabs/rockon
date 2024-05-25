from __future__ import annotations

from collections import Counter, defaultdict

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Sum
from django.http import HttpResponse
from django.template import loader

# from django.core.cache import cache
from django.views.decorators.cache import cache_page

from rockon.bands.models import Band


@login_required
@user_passes_test(lambda u: u.groups.filter(name="booking").exists())
@cache_page(60 * 5)
def booking_bide_overview(request):
    bands = (
        Band.objects.filter(event__id=request.session["current_event"])
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


# def get_data(request):
#     data = cache.get('band_bid_results')
#     if data is None:
#         bands = (
#             Band.objects.filter(event__id=request.session["current_event"])
#             .annotate(
#                 votes_count=Count("votes"),
#                 votes_sum=Sum("votes__vote"),
#                 votes_avg=Avg("votes__vote"),
#                 vote_counters=Count("votes__vote", distinct=True)
#             )
#             .order_by("-votes_sum", "-votes_avg", "track")
#         )
#         for index, band in enumerate(bands):
#             counters = defaultdict(int, Counter(band.votes.values_list("vote", flat=True)))
#             if not counters:
#                 continue
#             for i in range(6):
#                 counters[i]
#             counters = dict(sorted(counters.items()))
#             setattr(bands[index], "counters", dict(counters))
#         cache.set('band_bid_results', bands, 60 * 5)
#     return data
