from __future__ import annotations

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from rockon.base.models import Event, Organisation
from rockon.exhibitors.models import Asset, Attendance, Exhibitor


def join_forward(request):
    event = Event.objects.get(id=request.session["current_event"]).sub_events.first()
    return redirect("exhibitors:join_slug", slug=event.slug)


def join_slug(request, slug):
    if not request.user.is_authenticated:
        url = reverse("base:login_request")
        url += f"?ctx=exhibitors"
        return redirect(url)
    event = Event.objects.get(
        id=request.session.get("current_event")
    ).sub_events.first()
    if Exhibitor.objects.filter(
        organisation__members__in=[request.user], event=event
    ).exists():
        return redirect("exhibitors:join_submitted")
    template = loader.get_template("exhibitor_join.html")
    event = Event.objects.get(slug=slug)
    if not request.user.profile.is_profile_complete_exhibitor():
        template = loader.get_template("exhibitor_join_profile_incomplete.html")
        extra_context = {
            "site_title": "Profil unvollständig - Austelleranmeldung",
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


def signup_submitted(request):
    template = loader.get_template("exhibitor_signup_submitted.html")
    extra_context = {
        "site_title": "Anmeldung abgeschlossen",
    }
    return HttpResponse(template.render(extra_context, request))
