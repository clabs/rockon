from __future__ import annotations

from itertools import groupby
from operator import attrgetter

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.template import loader

from rockon.base.models import Event
from rockon.crew.models import (
    Attendance,
    AttendanceAddition,
    Crew,
    CrewMember,
    CrewMemberStatus,
    GuestListEntry,
)
from rockon.exhibitors.models import Exhibitor, ExhibitorAttendance, ExhibitorStatus


@login_required
@user_passes_test(lambda u: u.groups.filter(name="crew").exists())
def guestlist_entries(request) -> HttpResponse:
    template = loader.get_template("crew_guestlist_entries.html")
    event = Event.objects.get(id=request.session["current_event"])
    crew_member = CrewMember.objects.get(user=request.user, crew__event=event)
    guestlist_entries = crew_member.guestlist_entries.all().order_by("day")

    extra_context = {
        "event": event,
        "guestlist_entries": guestlist_entries,
        "site_title": "Gästeliste",
    }
    return HttpResponse(template.render(extra_context, request))
