from __future__ import annotations

from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from rockon.base.services import (
    build_switched_event_path,
    calculate_available_event_ids,
    get_request_account_context,
    get_selectable_event_by_slug,
)


@login_required
def switch_event(request, event_slug):
    """Validate the target event and redirect to the matching event-scoped view."""
    event = get_selectable_event_by_slug(event_slug)
    if event is None:
        messages.error(request, 'Event nicht gefunden.')
        return redirect(_get_default_redirect_path(request, None))

    user = request.user

    available_ids = [str(eid) for eid in calculate_available_event_ids(user)]
    if str(event.id) not in available_ids:
        messages.error(request, 'Du hast keinen Zugriff auf dieses Event.')
        return redirect(_get_default_redirect_path(request, event))

    messages.success(request, f'Event gewechselt zu: {event.name}')
    return redirect(_get_redirect_path(request, event))


def _get_redirect_path(request, event):
    next_path = _get_safe_next_path(request)
    if next_path and '/event/' in next_path:
        return build_switched_event_path(next_path, event)
    return _get_default_redirect_path(request, event)


def _get_default_redirect_path(request, event):
    account_context = request.GET.get('ctx') or get_request_account_context(request)

    if event is None:
        return reverse('crm_user_home')

    if account_context == 'bands':
        return reverse('bands:bid_router', kwargs={'slug': event.slug})

    if account_context == 'crew':
        return reverse('crew:join', kwargs={'slug': event.slug})

    if account_context == 'exhibitors':
        sub_event = event.sub_events.order_by('start').first()
        if sub_event is not None:
            return reverse('exhibitors:join', kwargs={'slug': sub_event.slug})

    return reverse('crm_user_home')


def _get_safe_next_path(request):
    next_path = request.GET.get('next')
    if not next_path:
        return None

    if not url_has_allowed_host_and_scheme(
        url=next_path,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return None

    parsed = urlparse(next_path)
    if parsed.scheme or parsed.netloc:
        return None

    return next_path
