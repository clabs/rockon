from __future__ import annotations

from django import template

from rockon.base.services.event_lookup import replace_event_slug_in_path

register = template.Library()


@register.simple_tag(takes_context=True)
def replace_event_slug(context, new_slug):
    """
    Replace the current event slug in request.path with a new event slug.

    Usage: {% replace_event_slug event.slug as new_path %}
    """
    request = context.get('request')

    if not request:
        return request.path if request else ''

    return replace_event_slug_in_path(request.path, new_slug)
