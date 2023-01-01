from __future__ import annotations

from django.http import JsonResponse
from django.shortcuts import redirect

from crm.models import LinkShortener


def link_shortener(request, slug):
    """Forards to the long form url."""
    try:
        link_shortener = LinkShortener.objects.get(slug=slug)
        link_shortener.counter += 1
        link_shortener.save()
        print(link_shortener.url)
        return redirect(link_shortener.url, permanent=False)
    except LinkShortener.DoesNotExist:
        # FIXME: this should be a redirect to a page that says "Token not found"
        return JsonResponse(
            {"status": "error", "message": "Token not found"}, status=404
        )
