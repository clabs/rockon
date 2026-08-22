from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from django.db.models import F
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.template import loader

from rockon.tools.models import LinkShortener


def _is_safe_redirect_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in ('http', 'https'):
        return False
    hostname = parsed.hostname or ''
    # Reject loopback / private IPs
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_loopback or ip.is_private or ip.is_link_local:
            return False
    except ValueError:
        # Not an IP address — check for localhost by name
        if hostname in ('localhost', ''):
            return False
    return True


def link_shortener(request, slug):
    """Forwards to the long form url."""
    try:
        link = LinkShortener.objects.get(slug=slug)
        if not _is_safe_redirect_url(link.url):
            return HttpResponseBadRequest('Invalid link target.')
        LinkShortener.objects.filter(slug=slug).update(counter=F('counter') + 1)
        return redirect(link.url, permanent=False)
    except LinkShortener.DoesNotExist:
        raise Http404('Der angefragte Link wurde nicht gefunden...')


def display_qr_code(request, slug):
    """Displays the QR code for the short form url."""
    try:
        template = loader.get_template('display_qr.html')
        link_shortener = LinkShortener.objects.get(slug=slug)
        extra_context = {'site_title': 'Shortlink QR', 'link_shortener': link_shortener}
        return HttpResponse(template.render(extra_context, request))
    except LinkShortener.DoesNotExist:
        raise Http404('Der angefragte Link wurde nicht gefunden...')
