from __future__ import annotations

from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template import loader

from tools.models import LinkShortener


def link_shortener(request, slug):
    """Forards to the long form url."""
    try:
        link_shortener = LinkShortener.objects.get(slug=slug)
        link_shortener.counter += 1
        link_shortener.save()
        return redirect(link_shortener.url, permanent=False)
    except LinkShortener.DoesNotExist:
        raise Http404("Der angefragte Link wurde nicht gefunden...")


def display_qr_code(request, slug):
    """Displays the QR code for the short form url."""
    try:
        template = loader.get_template("tools/display_qr.html")
        link_shortener = LinkShortener.objects.get(slug=slug)
        context = {"site_title": "Shortlink QR", "link_shortener": link_shortener}
        return HttpResponse(template.render(context, request))
    except LinkShortener.DoesNotExist:
        raise Http404("Der angefragte Link wurde nicht gefunden...")
