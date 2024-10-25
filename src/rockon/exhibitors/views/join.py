from __future__ import annotations

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from rockon.base.models import Event, Organisation
from rockon.exhibitors.models import Asset, Attendance, Exhibitor


def join(request, slug):
    if not request.user.is_authenticated:
        url = reverse("base:login_request")
        url += f"?ctx=exhibitors"
        return redirect(url)
    event = Event.objects.get(slug=slug).sub_events.first()
    template = loader.get_template("exhibitor_join.html")
    event = Event.objects.get(slug=slug)
    try:
        org = Organisation.objects.get(members__in=[request.user])
    except Organisation.DoesNotExist:
        org = None
    if org and Exhibitor.objects.filter(organisation=org, event=event).exists():
        return redirect("exhibitors:join_submitted", slug=slug)
    if not request.user.profile.is_profile_complete_exhibitor():
        template = loader.get_template("exhibitor_join_profile_incomplete.html")
        extra_context = {
            "site_title": "Profil unvollständig - Ausstelleranmeldung",
            "event": event,
            "slug": slug,
        }
        return HttpResponse(template.render(extra_context, request))
    template = loader.get_template("exhibitor_join.html")
    event = Event.objects.get(slug=slug)
    attendances = Attendance.objects.filter(event=event)
    assets = Asset.objects.all()
    extra_context = {
        "event": event,
        "site_title": "Anmeldung",
        "attendances": attendances,
        "assets": assets,
        "slug": slug,
        "org": org,
    }
    return HttpResponse(template.render(extra_context, request))


def signup(request, slug):
    template = loader.get_template("exhibitor_signup.html")
    event = Event.objects.get(slug=slug)
    attendances = Attendance.objects.filter(event=event)
    assets = Asset.objects.all()
    extra_context = {
        "event": event,
        "site_title": "Anmeldung",
        "attendances": attendances,
        "assets": assets,
        "slug": slug,
    }
    return HttpResponse(template.render(extra_context, request))


def signup_submitted(request, slug):
    template = loader.get_template("exhibitor_signup_submitted.html")
    extra_context = {
        "site_title": "Anmeldung abgeschlossen",
    }
    return HttpResponse(template.render(extra_context, request))
