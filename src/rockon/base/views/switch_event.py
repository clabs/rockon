from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from rockon.base.models import Event
from rockon.library.context_processors.available_events import (
    _calculate_available_event_ids,
    clear_available_events_cache,
)


@login_required
def switch_event(request, event_slug):
    """Switch the current event context for the user."""
    try:
        event = Event.objects.get(slug=event_slug, sub_event_of__isnull=True)
    except Event.DoesNotExist:
        messages.error(request, 'Event nicht gefunden.')
        return redirect('crm_user_home')

    user = request.user

    # Check access: the event must be in the user's list of available events
    available_ids = [str(eid) for eid in _calculate_available_event_ids(user)]
    if str(event.id) not in available_ids:
        messages.error(request, 'Du hast keinen Zugriff auf dieses Event.')
        return redirect('crm_user_home')

    _set_event_session(request, event)
    messages.success(request, f'Event gewechselt zu: {event.name}')
    return redirect('crm_user_home')


def _set_event_session(request, event):
    """Set the event in the session."""
    request.session['current_event_id'] = str(event.id)
    request.session['current_event_slug'] = event.slug
    request.session.modified = True
    clear_available_events_cache(request)
