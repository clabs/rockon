from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone

from rockon.base.services import get_current_event_for_request
from rockon.crew.models import Crew, CrewDate, CrewDateResponse


def _crew_dates_for_sidebar(request, event):
    if event is None:
        return []
    crew = Crew.objects.filter(event=event).first()
    if crew is None or not crew.is_member(request.user):
        return []

    crew_dates = list(
        CrewDate.objects.filter(crew=crew, date__gte=timezone.localdate())
        .order_by('date', 'start_time')
        .prefetch_related(
            Prefetch(
                'responses',
                queryset=CrewDateResponse.objects.filter(user=request.user),
                to_attr='my_responses',
            )
        )
    )
    for crew_date in crew_dates:
        crew_date.my_status = (
            crew_date.my_responses[0].status if crew_date.my_responses else ''
        )
    return crew_dates


@login_required
def home(request):
    """A view that returns the user homeview for logged in users."""
    event = get_current_event_for_request(request)
    crew_dates = _crew_dates_for_sidebar(request, event)

    template = loader.get_template('home.html')
    extra_context = {'site_title': 'Home', 'crew_dates': crew_dates}
    return HttpResponse(template.render(extra_context, request))
