from __future__ import annotations

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Sum
from django.http import HttpResponse
from django.template import loader

from rockon.bands.models import Band


@login_required
@user_passes_test(lambda u: u.groups.filter(name="booking").exists())
def booking_bide_overview(request):
    bands = (
        Band.objects.filter(event__id=request.session["current_event"])
        .annotate(
            votes_count=Count("votes"),
            votes_sum=Sum("votes__vote"),
            votes_avg=Avg("votes__vote"),
        )
        .order_by("-votes_sum", "-votes_avg", "track")
    )
    template = loader.get_template("booking/bid_overview.html")
    extra_context = {
        "site_title": "Bandbewertungen",
        "bands": bands,
    }
    return HttpResponse(template.render(extra_context, request))
