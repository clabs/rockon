from __future__ import annotations

from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from rockon.base.services import get_event_by_slug
from rockon.crew.models import CrewMember, CrewMemberStatus
from rockon.library.decorators import require_group


@require_group('crewcoord')
def crew_member_management(request, slug):
    template = loader.get_template('crewcoord_members.html')
    event = get_event_by_slug(slug)

    if request.method == 'POST' and event is not None:
        action = request.POST.get('action')
        filter_search_query = (request.POST.get('q') or '').strip()
        filter_state = (request.POST.get('state_filter') or '').strip()

        redirect_query = {}
        if filter_search_query:
            redirect_query['q'] = filter_search_query
        if filter_state:
            redirect_query['state'] = filter_state

        redirect_url = reverse('crew:coord_members', kwargs={'slug': slug})
        if redirect_query:
            redirect_url = f'{redirect_url}?{urlencode(redirect_query)}'

        if action == 'update_member_state':
            crew_member_id = request.POST.get('crew_member_id')
            state = request.POST.get('state')
            valid_states = {choice[0] for choice in CrewMemberStatus.choices}

            crew_member = (
                CrewMember.objects.filter(
                    id=crew_member_id,
                    crew__event=event,
                )
                .select_related('user')
                .first()
            )

            if crew_member is None:
                messages.error(request, 'Ungültiges Crewmitglied für dieses Event.')
            elif state not in valid_states:
                messages.error(request, 'Ungültiger Status.')
            else:
                crew_member.state = state
                crew_member.save(update_fields=['state'])
                messages.success(request, 'Crewmitgliedsstatus wurde aktualisiert.')
        elif action == 'update_member_arrived':
            crew_member_id = request.POST.get('crew_member_id')
            arrived_value = request.POST.get('arrived', '0')

            crew_member = (
                CrewMember.objects.filter(
                    id=crew_member_id,
                    crew__event=event,
                )
                .select_related('user')
                .first()
            )

            if crew_member is None:
                messages.error(request, 'Ungültiges Crewmitglied für dieses Event.')
            else:
                crew_member.arrived = arrived_value == '1'
                crew_member.save(update_fields=['arrived'])
                messages.success(request, 'Ankunftsstatus wurde aktualisiert.')
        else:
            messages.error(request, 'Unbekannte Aktion.')

        return redirect(redirect_url)

    member_states = list(CrewMemberStatus.choices)
    selected_state = (request.GET.get('state') or '').strip()
    search_query = (request.GET.get('q') or '').strip()
    valid_states = {choice[0] for choice in member_states}

    members = []
    if event is not None:
        member_qs = CrewMember.objects.filter(crew__event=event)

        if selected_state and selected_state in valid_states:
            member_qs = member_qs.filter(state=selected_state)
        else:
            selected_state = ''

        if search_query:
            member_qs = member_qs.filter(
                Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
            )

        members = list(
            member_qs.select_related('user', 'crew', 'shirt').order_by(
                'user__last_name',
                'user__first_name',
            )
        )

    extra_context = {
        'event': event,
        'event_slug': slug,
        'site_title': 'Crewmitglieder',
        'members': members,
        'member_states': member_states,
        'selected_state': selected_state,
        'search_query': search_query,
    }
    return HttpResponse(template.render(extra_context, request))
