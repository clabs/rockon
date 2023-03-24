from __future__ import annotations

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.http import HttpResponse
from django.template import loader

from crew.models import (
    Attendance,
    AttendanceAddition,
    Crew,
    CrewMember,
    CrewMemberStatus,
)
from event.models import Event
from exhibitors.models import Exhibitor, ExhibitorAttendance, ExhibitorStatus


@login_required
@user_passes_test(lambda u: u.groups.filter(name="catering_food").exists())
def attendance_table(request):
    template = loader.get_template("crew/kitchen_attendance.html")
    try:
        event = Event.objects.get(is_current=True)
    except Event.DoesNotExist:
        event = None
    attendances = Attendance.objects.filter(event=event)
    crew = Crew.objects.filter(event=event)
    crew_members = CrewMember.objects.filter(crew__in=crew).exclude(
        state__in=[CrewMemberStatus.UNKNOWN, CrewMemberStatus.REJECTED]
    )
    kitchen_list = []
    nutrion_notes = [crew_member.nutrition_note for crew_member in crew_members]
    addtion_list = []

    exhibitors = []

    for sub_event in event.sub_events.all():
        exhibitors += Exhibitor.objects.filter(
            event=sub_event, state=ExhibitorStatus.CONFIRMED
        )

    # FIXME: this query does not really scale well. :(
    for day in attendances:
        amounts = {}
        misc_additions = AttendanceAddition.objects.filter(attendance=day)
        amounts["misc"] = misc_additions.aggregate(Sum("amount"))["amount__sum"] or 0
        additions = [
            {"comment": item.comment, "amount": item.amount} for item in misc_additions
        ]

        exhibitor_attendance_for_day = ExhibitorAttendance.objects.filter(
            exhibitor__in=exhibitors, day__day=day.day
        )
        for exhibitor_attendance in exhibitor_attendance_for_day:
            additions.append(
                {
                    "comment": exhibitor_attendance.exhibitor,
                    "amount": exhibitor_attendance.count,
                }
            )
            amounts["misc"] += exhibitor_attendance.count

        if additions:
            addtion_list.append({"day": day, "additions": additions})

        amounts["day"] = day
        amounts["omnivore"] = (
            crew_members.filter(attendance=day, nutrition="omnivore").count() or 0
        )
        amounts["vegetarian"] = (
            crew_members.filter(attendance=day, nutrition="vegetarian").count() or 0
        )
        amounts["vegan"] = (
            crew_members.filter(attendance=day, nutrition="vegan").count() or 0
        )
        amounts["sum"] = (crew_members.filter(attendance=day).count() or 0) + amounts[
            "misc"
        ]

        amounts["omnivore_overnight"] = (
            crew_members.filter(
                attendance=day, nutrition="omnivore", stays_overnight=True
            ).count()
            or 0  # noqa: W503
        )
        amounts["vegetarian_overnight"] = (
            crew_members.filter(
                attendance=day, nutrition="vegetarian", stays_overnight=True
            ).count()
            or 0  # noqa: W503
        )
        amounts["vegan_overnight"] = (
            crew_members.filter(
                attendance=day, nutrition="vegan", stays_overnight=True
            ).count()
            or 0  # noqa: W503
        )
        amounts["sum_overnight"] = (
            crew_members.filter(attendance=day, stays_overnight=True).count() or 0
        )

        kitchen_list.append(amounts)

    extra_context = {
        "event": event,
        "kitchen_list": kitchen_list,
        "nutrion_notes": nutrion_notes,
        "addtion_list": addtion_list,
        "site_title": "Mengenliste",
    }
    return HttpResponse(template.render(extra_context, request))
