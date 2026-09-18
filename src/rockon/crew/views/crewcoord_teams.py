from __future__ import annotations

from collections import defaultdict

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from rockon.base.services import get_event_by_slug
from rockon.crew.models import CrewMember, EventTeam, TeamMember, TeamMemberState
from rockon.crew.services import clear_invalid_team_roles
from rockon.library.decorators import require_group

_STATE_ICON_CLASS = {
    TeamMemberState.UNKNOWN: 'fa-question',
    TeamMemberState.CONFIRMED: 'fa-check',
    TeamMemberState.REJECTED: 'fa-xmark',
}
_STATE_BUTTON_CLASS = {
    TeamMemberState.UNKNOWN: 'btn-secondary',
    TeamMemberState.CONFIRMED: 'btn-success',
    TeamMemberState.REJECTED: 'btn-danger',
}
_STATE_LABEL = dict(TeamMemberState.choices)


@require_group('crewcoord')
def crew_team_management(request, slug):
    template = loader.get_template('crewcoord_teams.html')
    event = get_event_by_slug(slug)

    if request.method == 'POST' and event is not None:
        action = request.POST.get('action')

        with transaction.atomic():
            if action == 'set_team_roles':
                event_team_id = request.POST.get('event_team_id')
                lead_raw = request.POST.get('lead_id') or None
                vize_lead_raw = request.POST.get('vize_lead_id') or None
                invalid_role_input = False

                try:
                    lead_id = int(lead_raw) if lead_raw is not None else None
                    vize_lead_id = (
                        int(vize_lead_raw) if vize_lead_raw is not None else None
                    )
                except TypeError, ValueError:
                    messages.error(
                        request,
                        'Ungültige Auswahl für Teamleitung oder Stellvertretung.',
                    )
                    invalid_role_input = True
                    lead_id = None
                    vize_lead_id = None

                event_team = EventTeam.objects.filter(
                    id=event_team_id, event=event
                ).first()

                if event_team is None:
                    messages.error(request, 'Ungültiges Team für dieses Event.')
                elif invalid_role_input:
                    clear_invalid_team_roles(event_team)
                else:
                    confirmed_user_ids = set(
                        TeamMember.objects.filter(
                            event_team=event_team,
                            state=TeamMemberState.CONFIRMED,
                        ).values_list('crewmember__user_id', flat=True)
                    )

                    if lead_id is not None and lead_id not in confirmed_user_ids:
                        clear_invalid_team_roles(event_team)
                        messages.error(
                            request,
                            'Teamleitung muss ein bestätigtes Teammitglied sein.',
                        )
                    elif (
                        vize_lead_id is not None
                        and vize_lead_id not in confirmed_user_ids
                    ):
                        clear_invalid_team_roles(event_team)
                        messages.error(
                            request,
                            'Stellvertretung muss ein bestätigtes Teammitglied sein.',
                        )
                    else:
                        event_team.lead_id = lead_id
                        event_team.vize_lead_id = vize_lead_id
                        event_team.save(update_fields=['lead', 'vize_lead'])
                        clear_invalid_team_roles(event_team)
                        messages.success(request, 'Teamleitung wurde aktualisiert.')
            else:
                messages.error(request, 'Unbekannte Aktion.')

        return redirect('crew:coord_teams', slug=slug)

    crew_members = []
    event_teams = []
    matrix_rows = []
    teams_context = []

    if event is not None:
        crew_members = list(
            CrewMember.objects.filter(crew__event=event)
            .select_related('user')
            .order_by('user__last_name', 'user__first_name')
        )

        event_teams = list(
            EventTeam.objects.filter(event=event)
            .select_related('team', 'team__category', 'lead', 'vize_lead')
            .order_by('team__category__name', 'team__name')
        )

        team_members = list(
            TeamMember.objects.filter(event_team__event=event).select_related(
                'crewmember__user'
            )
        )

        state_by_key = {
            (team_member.crewmember_id, team_member.event_team_id): team_member.state
            for team_member in team_members
        }

        confirmed_members_by_event_team = defaultdict(list)
        for team_member in team_members:
            if team_member.state == TeamMemberState.CONFIRMED:
                confirmed_members_by_event_team[team_member.event_team_id].append(
                    team_member
                )

        for crew_member in crew_members:
            cells = []
            for event_team in event_teams:
                state = state_by_key.get(
                    (crew_member.id, event_team.id), TeamMemberState.UNKNOWN
                )
                cells.append(
                    {
                        'event_team_id': event_team.id,
                        'crewmember_id': crew_member.id,
                        'team_name': event_team.team.name,
                        'state': state,
                        'icon_class': _STATE_ICON_CLASS[state],
                        'button_class': _STATE_BUTTON_CLASS[state],
                        'state_label': _STATE_LABEL[state],
                    }
                )
            matrix_rows.append({'crew_member': crew_member, 'cells': cells})

        for event_team in event_teams:
            teams_context.append(
                {
                    'event_team': event_team,
                    'confirmed_members': sorted(
                        confirmed_members_by_event_team[event_team.id],
                        key=lambda member: (
                            member.crewmember.user.last_name,
                            member.crewmember.user.first_name,
                        ),
                    ),
                }
            )

    extra_context = {
        'event': event,
        'site_title': 'Teamverwaltung',
        'event_teams': event_teams,
        'matrix_rows': matrix_rows,
        'teams': teams_context,
    }
    return HttpResponse(template.render(extra_context, request))
