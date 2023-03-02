from __future__ import annotations

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.generic.base import TemplateView

from event.models import Event


def custom_bad_request_view(request, exception=None):
    context = {"site_title": "Fehler 400", "reason": exception}
    return render(request, "errors/400.html", context, status=400)


def custom_permission_denied_view(request, exception=None):
    context = {"site_title": "Fehler 403", "reason": exception}
    return render(request, "errors/403.html", context, status=403)


def custom_page_not_found_view(request, exception):
    context = {"site_title": "Fehler 404", "reason": exception}
    return render(request, "errors/404.html", context, status=404)


def custom_error_view(request, exception=None):
    context = {"site_title": "Fehler 500", "reason": exception}
    return render(request, "errors/500.html", context, status=500)


class ImprintView(TemplateView):
    template_name = "rockon/imprint.html"
    extra_context = {"site_title": "Impressum"}


class PrivacyView(TemplateView):
    template_name = "rockon/privacy.html"
    extra_context = {"site_title": "Privacy Policy"}


def index_view(request):
    template = loader.get_template("rockon/landing_index.html")
    events = Event.objects.filter(show_on_landing_page=True)
    extra_context = {"site_title": "Start", "events": events}
    return HttpResponse(template.render(extra_context, request))
