from __future__ import annotations

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.http import HttpResponse
from django.template import loader

from rockon.base.models import Event
from rockon.crew.models import Attendance, Crew, CrewMember, CrewMemberStatus, Shirt


@login_required
@user_passes_test(lambda u: u.groups.filter(name="crewcoord").exists())
def crew_chart(request):
    template = loader.get_template("crew_overview.html")
    try:
        event = Event.objects.get(id=request.session["current_event"])
        attendances = (
            Attendance.objects.filter(
                event=event,
                crew_members__state__in=[
                    CrewMemberStatus.CONFIRMED,
                    CrewMemberStatus.ARRIVED,
                ],
            )
            .order_by("day")
            .annotate(no_of_crew_members=Count("crew_members"))
        )
        attendances_unknown = (
            Attendance.objects.filter(
                event=event,
                crew_members__state__in=[
                    CrewMemberStatus.UNKNOWN,
                    CrewMemberStatus.REJECTED,
                ],
            )
            .order_by("day")
            .annotate(no_of_crew_members=Count("crew_members"))
        )
    except Event.DoesNotExist:
        event = None
        attendances = None

    extra_context = {
        "event": event,
        "site_title": "Übersicht",
        "attendances_unknown": attendances_unknown,
        "attendances": attendances,
    }
    return HttpResponse(template.render(extra_context, request))


@login_required
@user_passes_test(lambda u: u.groups.filter(name="crewcoord").exists())
def crew_shirts(request):
    template = loader.get_template("crewcoord_tshirts.html")
    try:
        event = Event.objects.get(id=request.session["current_event"])
        crews = Crew.objects.filter(event=event)
        crew_members = CrewMember.objects.filter(crew__in=crews).exclude(
            state__in=[CrewMemberStatus.UNKNOWN, CrewMemberStatus.REJECTED]
        )

        shirts = Shirt.objects.all()

        shirt_counts = crew_members.values("shirt").annotate(
            shirt_count=Count("shirt"),
        )

        counts = []
        for shirt in shirts:
            shirt_count = shirt_counts.filter(shirt=shirt.id).values("shirt_count")
            try:
                amount = shirt_count[0]["shirt_count"]
            except IndexError:
                amount = 0
            counts.append({"shirt": shirt, "count": amount})
    except Event.DoesNotExist:
        counts = None
        crew_members = None

    extra_context = {
        "event": event,
        "site_title": "T-Shirts",
        "counts": counts,
        "sum": sum([count["count"] for count in counts]),
        "crew_members": crew_members,
    }
    return HttpResponse(template.render(extra_context, request))
