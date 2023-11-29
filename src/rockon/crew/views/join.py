from __future__ import annotations

from datetime import date, timedelta

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from rockon.base.models import Event
from rockon.crew.models import Attendance, Shirt, Skill, TeamCategory
from rockon.crew.models.crew_member import CrewMember


def join_forward(request):
    event = Event.objects.get(id=request.session["current_event"])
    return redirect("crew:join_slug", slug=event.slug)


def join_slug(request, slug):
    if not request.user.is_authenticated:
        url = reverse("base:login_request")
        url += f"?ctx=crew"
        return redirect(url)
    if CrewMember.objects.filter(user=request.user).exists():
        return redirect("crew:join_submitted")
    template = loader.get_template("join.html")
    event = Event.objects.get(slug=slug)
    if not request.user.profile.is_profile_complete_crew():
        template = loader.get_template("join_profile_incomplete.html")
        extra_context = {
            "site_title": "Profil unvollständig - Crewanmeldung",
            "event": event,
            "slug": slug,
        }
        return HttpResponse(template.render(extra_context, request))

    shirts = Shirt.objects.all()
    skills = Skill.objects.all()
    attendance_phases = Attendance.get_phases(event=event)
    team_categories = TeamCategory.objects.all()
    allow_overnight = False
    if request.user.profile.birthday:
        allow_overnight = request.user.profile.birthday < date.today() - timedelta(
            days=18 * 365
        )
    extra_context = {
        "event": event,
        "og_title": f"Crewanmeldung {event.name}",
        "og_description": f"Crewanmeldung für die Veranstaltung {event.name}, sei Teil des Teams!",
        "shirts": shirts,
        "site_title": f"Crewanmeldung {event.name}",
        "skills": skills,
        "slug": slug,
        "team_categories": team_categories,
        "attendance_phases": attendance_phases,
        "allow_overnight": allow_overnight,
    }
    return HttpResponse(template.render(extra_context, request))


def join_submitted(request):
    template = loader.get_template("join_submitted.html")
    extra_context = {"site_title": "Anmeldung abgeschlossen"}
    return HttpResponse(template.render(extra_context, request))
