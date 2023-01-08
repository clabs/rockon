from __future__ import annotations

from math import copysign

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django_q.tasks import async_task, result

from crew.models import Attendance, Shirt, Skill, Team
from event.models import Event


def signup_root(request, slug):
    return redirect("crew_preselect", slug=slug)


def preselect(request, slug):
    template = loader.get_template("crew/preselect.html")
    context = {
        "site_title": "Vorauswahl",
        "slug": slug,
    }
    task_id = async_task(copysign, 2, -1)
    task_result = result(task_id, 200)
    print(task_result)
    return HttpResponse(template.render(context, request))


def signup(request, slug):
    template = loader.get_template("crew/signup.html")
    event = Event.objects.get(slug=slug)
    shirts = Shirt.objects.all()
    skills = Skill.objects.all()
    attendance_phases = Attendance.get_phases(event=event)
    teams = Team.objects.filter(is_public=True)
    context = {
        "event": event,
        "shirts": shirts,
        "site_title": "Anmeldung",
        "skills": skills,
        "slug": slug,
        "teams": teams,
        "attendance_phases": attendance_phases,
    }
    return HttpResponse(template.render(context, request))


def signup_submitted(request, slug):
    template = loader.get_template("crew/signup_submitted.html")
    context = {
        "site_title": "Anmeldung abgeschlossen",
        "slug": slug,
    }
    return HttpResponse(template.render(context, request))
