from __future__ import annotations

from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.generic.detail import DetailView

from crew.models import Attendance, Crew, Shirt, Skill, TeamCategory
from crew.models.crew_member import CrewMember
from event.models import Event


def signup_root(request):
    event = Event.objects.filter(is_current=True).first()
    return redirect("crew_slug", slug=event.slug)


def signup_slug(request, slug):
    if request.user.is_authenticated:
        return redirect("crew_signup_form", slug=slug)
    template = loader.get_template("preselect.html")
    extra_context = {"site_title": "Vorauswahl", "slug": slug}
    return HttpResponse(template.render(extra_context, request))


@login_required
def signup(request, slug):
    template = loader.get_template("signup.html")
    event = Event.objects.get(slug=slug)
    if CrewMember.objects.filter(user=request.user).exists():
        return redirect("crew_signup_form_submitted", slug=slug)
    shirts = Shirt.objects.all()
    skills = Skill.objects.all()
    attendance_phases = Attendance.get_phases(event=event)
    team_categories = TeamCategory.objects.all()
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


class SignupSubmittedView(LoginRequiredMixin, DetailView):
    template_name = "signup_submitted.html"
    extra_context = {"site_title": "Anmeldung abgeschlossen"}
    query_pk_and_slug = "slug"
    model = Event
