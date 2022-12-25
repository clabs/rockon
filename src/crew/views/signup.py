from __future__ import annotations

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from event.models import Event
from crew.models import Shirt
from crew.models import Skill
from crew.models import Attendance
from crew.models import Team


def signup_root(request, slug):
    return redirect("crew_preselect", slug=slug)


def preselect(request, slug):
    template = loader.get_template("crew/preselect.html")
    context = {
        "site_title": "Vorauswahl",
        "slug": slug,
    }
    return HttpResponse(template.render(context, request))


def signup(request, slug):
    template = loader.get_template("crew/signup.html")
    event = Event.objects.get(slug=slug)
    shirts = Shirt.objects.all()
    skills = Skill.objects.all()
    attendance = Attendance.objects.filter(event=event)
    teams = Team.objects.filter(is_public=True)
    context = {
        "attendance": attendance,
        "event": event,
        "shirts": shirts,
        "site_title": "Anmeldung",
        "skills": skills,
        "slug": slug,
        "teams": teams,
    }
    return HttpResponse(template.render(context, request))


def signup_submitted(request, slug):
    template = loader.get_template("crew/signup_submitted.html")
    context = {
        "site_title": "Anmeldung abgeschlossen",
        "slug": slug,
    }
    return HttpResponse(template.render(context, request))
