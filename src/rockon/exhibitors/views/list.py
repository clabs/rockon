from __future__ import annotations

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from rockon.base.services import get_event_by_slug
from rockon.exhibitors.models import Exhibitor, ExhibitorStatus


@login_required
@user_passes_test(lambda u: u.groups.filter(name='exhibitor_admins').exists())
def exhibitor_list(request, slug):
    template = loader.get_template('exhibitor_list.html')
    event = get_event_by_slug(slug)

    if event is None:
        return HttpResponse(status=404)

    if request.method == 'POST':
        action = request.POST.get('action')
        filter_search_query = (request.POST.get('q') or '').strip()
        filter_state = (request.POST.get('state_filter') or '').strip()

        redirect_query = {}
        if filter_search_query:
            redirect_query['q'] = filter_search_query
        if filter_state:
            redirect_query['state'] = filter_state

        redirect_url = reverse('exhibitors:exhibitor_list', kwargs={'slug': slug})
        if redirect_query:
            redirect_url = f'{redirect_url}?{urlencode(redirect_query)}'

        if action == 'update_exhibitor_state':
            exhibitor_id = request.POST.get('exhibitor_id')
            state = request.POST.get('state')
            valid_states = {choice[0] for choice in ExhibitorStatus.choices}

            exhibitor = (
                Exhibitor.objects.filter(id=exhibitor_id, event=event)
                .select_related('organisation')
                .first()
            )

            if exhibitor is None:
                messages.error(request, 'Ungültiger Aussteller für dieses Event.')
            elif state not in valid_states:
                messages.error(request, 'Ungültiger Status.')
            else:
                exhibitor.state = state
                exhibitor.save(update_fields=['state'])
                messages.success(request, 'Ausstellerstatus wurde aktualisiert.')
        else:
            messages.error(request, 'Unbekannte Aktion.')

        return redirect(redirect_url)

    exhibitor_states = list(ExhibitorStatus.choices)
    selected_state = (request.GET.get('state') or '').strip()
    search_query = (request.GET.get('q') or '').strip()
    valid_states = {choice[0] for choice in exhibitor_states}

    exhibitor_qs = Exhibitor.objects.filter(event=event)

    if selected_state and selected_state in valid_states:
        exhibitor_qs = exhibitor_qs.filter(state=selected_state)
    else:
        selected_state = ''

    if search_query:
        exhibitor_qs = exhibitor_qs.filter(
            Q(organisation__org_name__icontains=search_query)
        )

    exhibitors = list(
        exhibitor_qs.select_related('organisation').order_by(
            'organisation__org_name',
        )
    )

    extra_context = {
        'exhibitors': exhibitors,
        'exhibitor_states': exhibitor_states,
        'selected_state': selected_state,
        'search_query': search_query,
        'event': event,
        'event_slug': slug,
    }
    return HttpResponse(template.render(extra_context, request))
