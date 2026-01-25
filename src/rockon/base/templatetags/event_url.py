from __future__ import annotations

import re
from urllib.parse import quote

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def replace_event_slug(context, new_slug):
    """
    Replace the current event slug in request.path with a new event slug.

    Usage: {% replace_event_slug event.slug as new_path %}
    """
    request = context.get('request')
    current_event = context.get('current_event')

    if not request or not current_event:
        return request.path if request else ''

    path = request.path
    old_slug = current_event.slug

    if old_slug and new_slug and old_slug != new_slug:
        slug_re = re.compile(r'^[A-Za-z0-9_-]+$')
        if slug_re.fullmatch(new_slug):
            new_slug_safe = new_slug
        else:
            new_slug_safe = quote(new_slug, safe='-_')

        path = re.sub(
            rf'/event/{re.escape(old_slug)}/',
            lambda m: f'/event/{new_slug_safe}/',
            path,
        )
        path = re.sub(
            rf'/events/{re.escape(old_slug)}/',
            lambda m: f'/events/{new_slug_safe}/',
            path,
        )

    return path
