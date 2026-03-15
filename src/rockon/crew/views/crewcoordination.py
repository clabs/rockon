from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from rockon.base.models import Event
from rockon.crew.models import (
    Attendance,
    Crew,
    CrewMember,
    CrewMemberStatus,
    EventTeam,
    Shirt,
    TeamMember,
    TeamMemberState,
)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='crewcoord').exists())
def crew_chart(request, slug):
    template = loader.get_template('crew_overview.html')
    try:
        event = Event.objects.get(slug=slug)
        attendances = (
            Attendance.objects.filter(
                event=event,
                crew_members__state__in=[
                    CrewMemberStatus.CONFIRMED,
                    CrewMemberStatus.ARRIVED,
                ],
            )
            .order_by('day')
            .annotate(no_of_crew_members=Count('crew_members'))
        )
        attendances_unknown = (
            Attendance.objects.filter(
                event=event,
                crew_members__state__in=[
                    CrewMemberStatus.UNKNOWN,
                    CrewMemberStatus.REJECTED,
                ],
            )
            .order_by('day')
            .annotate(no_of_crew_members=Count('crew_members'))
        )
    except Event.DoesNotExist:
        event = None
        attendances = None

    extra_context = {
        'event': event,
        'site_title': 'Übersicht',
        'attendances_unknown': attendances_unknown,
        'attendances': attendances,
    }
    return HttpResponse(template.render(extra_context, request))


@login_required
@user_passes_test(lambda u: u.groups.filter(name='crewcoord').exists())
def crew_shirts(request, slug):
    template = loader.get_template('crewcoord_tshirts.html')
    try:
        event = Event.objects.get(slug=slug)
        crews = Crew.objects.filter(event=event)
        crew_members = CrewMember.objects.filter(crew__in=crews).exclude(
            state__in=[CrewMemberStatus.UNKNOWN, CrewMemberStatus.REJECTED]
        )

        shirts = Shirt.objects.all()

        shirt_counts_qs = crew_members.values('shirt').annotate(
            shirt_count=Count('shirt'),
        )
        shirt_count_map = {
            item['shirt']: item['shirt_count'] for item in shirt_counts_qs
        }
        counts = [
            {'shirt': shirt, 'count': shirt_count_map.get(shirt.id, 0)}
            for shirt in shirts
        ]
    except Event.DoesNotExist:
        counts = None
        crew_members = None

    extra_context = {
        'event': event,
        'site_title': 'T-Shirts',
        'counts': counts,
        'sum': sum([count['count'] for count in counts]),
        'crew_members': crew_members,
    }
    return HttpResponse(template.render(extra_context, request))


def _clear_invalid_team_roles(event_team: EventTeam) -> None:
    confirmed_user_ids = set(
        TeamMember.objects.filter(
            event_team=event_team,
            state=TeamMemberState.CONFIRMED,
        ).values_list('crewmember__user_id', flat=True)
    )

    update_fields = []
    if event_team.lead_id and event_team.lead_id not in confirmed_user_ids:
        event_team.lead = None
        update_fields.append('lead')
    if event_team.vize_lead_id and event_team.vize_lead_id not in confirmed_user_ids:
        event_team.vize_lead = None
        update_fields.append('vize_lead')

    if update_fields:
        event_team.save(update_fields=update_fields)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='crewcoord').exists())
def crew_team_management(request, slug):
    template = loader.get_template('crewcoord_teams.html')

    try:
        event = Event.objects.get(slug=slug)
    except Event.DoesNotExist:
        event = None

    if request.method == 'POST' and event is not None:
        action = request.POST.get('action')

        with transaction.atomic():
            if action == 'update_member_state':
                team_member_id = request.POST.get('team_member_id')
                state = request.POST.get('state')
                valid_states = {choice[0] for choice in TeamMemberState.choices}

                team_member = (
                    TeamMember.objects.select_related('event_team')
                    .filter(
                        id=team_member_id,
                        event_team__event=event,
                    )
                    .first()
                )

                if team_member is None:
                    messages.error(request, 'Ungültiges Teammitglied für dieses Event.')
                elif state not in valid_states:
                    messages.error(request, 'Ungültiger Status.')
                else:
                    team_member.state = state
                    team_member.save(update_fields=['state'])
                    _clear_invalid_team_roles(team_member.event_team)
                    messages.success(request, 'Mitgliedsstatus wurde aktualisiert.')

            elif action == 'set_team_roles':
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
                    _clear_invalid_team_roles(event_team)
                else:
                    confirmed_user_ids = set(
                        TeamMember.objects.filter(
                            event_team=event_team,
                            state=TeamMemberState.CONFIRMED,
                        ).values_list('crewmember__user_id', flat=True)
                    )

                    if lead_id is not None and lead_id not in confirmed_user_ids:
                        _clear_invalid_team_roles(event_team)
                        messages.error(
                            request,
                            'Teamleitung muss ein bestätigtes Teammitglied sein.',
                        )
                    elif (
                        vize_lead_id is not None
                        and vize_lead_id not in confirmed_user_ids
                    ):
                        _clear_invalid_team_roles(event_team)
                        messages.error(
                            request,
                            'Stellvertretung muss ein bestätigtes Teammitglied sein.',
                        )
                    else:
                        event_team.lead_id = lead_id
                        event_team.vize_lead_id = vize_lead_id
                        event_team.save(update_fields=['lead', 'vize_lead'])
                        _clear_invalid_team_roles(event_team)
                        messages.success(request, 'Teamleitung wurde aktualisiert.')
            else:
                messages.error(request, 'Unbekannte Aktion.')

        return redirect('crew:coord_teams', slug=slug)

    event_teams_qs = (
        EventTeam.objects.filter(event=event)
        .select_related('team', 'lead', 'vize_lead')
        .prefetch_related(
            'members__crewmember__user',
        )
    )
    event_teams = list(event_teams_qs)

    teams_context = []
    for event_team in event_teams:
        members = sorted(
            event_team.members.all(),
            key=lambda member: (
                member.crewmember.user.last_name,
                member.crewmember.user.first_name,
            ),
        )
        confirmed_members = [
            member for member in members if member.state == TeamMemberState.CONFIRMED
        ]
        teams_context.append(
            {
                'event_team': event_team,
                'members': members,
                'confirmed_members': confirmed_members,
            }
        )

    extra_context = {
        'event': event,
        'site_title': 'Teamverwaltung',
        'teams': teams_context,
        'member_states': TeamMemberState.choices,
    }
    return HttpResponse(template.render(extra_context, request))
