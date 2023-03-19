from __future__ import annotations

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.http import HttpResponse
from django.template import loader

from crew.models import Attendance
from event.models import Event


@login_required
@user_passes_test(lambda u: u.groups.filter(name="crewcoord").exists())
def crew_chart(request):
    template = loader.get_template("crew/crewcoord_overview.html")
    event = Event.objects.get(is_current=True)
    attendances = Attendance.objects.filter(event=event).annotate(
        no_of_crew_members=Count("crew_members")
    )
    for attendance in attendances:
        print(attendance.no_of_crew_members)

    extra_context = {
        "event": event,
        "site_title": "Übersicht",
        "attendances": attendances,
    }
    return HttpResponse(template.render(extra_context, request))
