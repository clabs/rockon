from __future__ import annotations

from django.http import Http404
from django.shortcuts import redirect

from crm.models import LinkShortener


def link_shortener(request, slug):
    """Forards to the long form url."""
    try:
        link_shortener = LinkShortener.objects.get(slug=slug)
        link_shortener.counter += 1
        link_shortener.save()
        return redirect(link_shortener.url, permanent=False)
    except LinkShortener.DoesNotExist:
        raise Http404("Der angefrate Schlüssel wurde nicht gefunden...")
