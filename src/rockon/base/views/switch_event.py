from __future__ import annotations

import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme

from rockon.base.models import Event
from rockon.crew.models import CrewMember
from rockon.exhibitors.models import Exhibitor


def _get_redirect_url(request, old_slug, new_slug):
    """Get safe redirect URL from 'next' parameter, replacing old event slug with new one."""
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        if old_slug and new_slug and old_slug != new_slug:
            next_url = re.sub(
                rf'/event/{re.escape(old_slug)}/',
                f'/event/{new_slug}/',
                next_url,
            )
            next_url = re.sub(
                rf'/events/{re.escape(old_slug)}/',
                f'/events/{new_slug}/',
                next_url,
            )
        return next_url
    return 'crm_user_home'


@login_required
def switch_event(request, event_slug):
    """Switch the current event context for the user."""
    old_slug = request.session.get('current_event_slug')

    try:
        event = Event.objects.get(slug=event_slug, sub_event_of__isnull=True)
    except Event.DoesNotExist:
        messages.error(request, 'Event nicht gefunden.')
        redirect_url = _get_redirect_url(request, None, None)
        return redirect(redirect_url)

    redirect_url = _get_redirect_url(request, old_slug, event.slug)
    user = request.user

    if user.is_staff:
        _set_event_session(request, event)
        messages.success(request, f'Event gewechselt zu: {event.name}')
        return redirect(redirect_url)

    has_access = False

    if user.groups.filter(name='crew').exists():
        has_crew_access = CrewMember.objects.filter(
            user=user,
            crew__event=event,
            state__in=['confirmed', 'arrived'],
        ).exists()
        if has_crew_access:
            has_access = True

    if user.groups.filter(name='exhibitors').exists():
        org_ids = user.organisations.values_list('id', flat=True)
        has_exhibitor_access = Exhibitor.objects.filter(
            organisation_id__in=org_ids,
            event__in=[event] + list(event.sub_events.all()),
        ).exists()
        if has_exhibitor_access:
            has_access = True

    if not has_access:
        messages.error(request, 'Du hast keinen Zugriff auf dieses Event.')
        return redirect(redirect_url)

    _set_event_session(request, event)
    messages.success(request, f'Event gewechselt zu: {event.name}')
    return redirect(redirect_url)


def _set_event_session(request, event):
    """Set the event in the session."""
    request.session['current_event_id'] = str(event.id)
    request.session['current_event_slug'] = event.slug
