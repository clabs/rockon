from __future__ import annotations

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from crew.models import Attendance, Shirt, Skill, TeamCategory
from event.models import Event


def signup_root(request, slug):
    return redirect("crew_preselect", slug=slug)


class PreselectView(TemplateView):
    template_name = "crew/preselect.html"
    extra_context = {"site_title": "Vorauswahl"}


def signup(request, slug):
    template = loader.get_template("crew/signup.html")
    event = Event.objects.get(slug=slug)
    shirts = Shirt.objects.all()
    skills = Skill.objects.all()
    attendance_phases = Attendance.get_phases(event=event)
    team_categories = TeamCategory.objects.all()
    context = {
        "event": event,
        "shirts": shirts,
        "site_title": "Anmeldung",
        "skills": skills,
        "slug": slug,
        "team_categories": team_categories,
        "attendance_phases": attendance_phases,
    }
    return HttpResponse(template.render(context, request))


class SignupSubmittedView(DetailView):
    template_name = "crew/signup_submitted.html"
    extra_context = {"site_title": "Anmeldung abgeschlossen"}
    query_pk_and_slug = "slug"
    model = Event
