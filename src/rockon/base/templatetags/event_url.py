from __future__ import annotations

import re

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
        path = re.sub(
            rf'/event/{re.escape(old_slug)}/',
            f'/event/{new_slug}/',
            path,
        )
        path = re.sub(
            rf'/events/{re.escape(old_slug)}/',
            f'/events/{new_slug}/',
            path,
        )

    return path
