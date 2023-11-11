from __future__ import annotations

from django.http import HttpResponse
from django.template import loader

from rockon.event.models import Event
from rockon.exhibitors.models import Asset, Attendance


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
        "slug": slug,
    }
    return HttpResponse(template.render(extra_context, request))