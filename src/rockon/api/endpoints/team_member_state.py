from __future__ import annotations

from django.db import transaction
from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.status import StatusOut
from rockon.api.schemas.team_member_state import TeamMemberStateIn, TeamMemberStateOut
from rockon.crew.models import CrewMember, EventTeam, TeamMember, TeamMemberState
from rockon.crew.services import clear_invalid_team_roles

teamMemberState = Router()


@teamMemberState.patch(
    '/{slug}/',
    response={200: TeamMemberStateOut, 400: StatusOut, 403: StatusOut, 404: StatusOut},
    url_name='team_member_state_update',
    auth=django_auth,
)
def update_team_member_state(request, slug: str, data: TeamMemberStateIn):
    """Create or update a crewmember's team-membership state (crewcoord only)."""
    if not request.user.groups.filter(name='crewcoord').exists():
        return 403, {'status': 'error', 'message': 'Not authorized'}

    if data.state not in TeamMemberState.values:
        return 400, {'status': 'error', 'message': 'Invalid status'}

    try:
        event_team = EventTeam.objects.get(id=data.event_team_id, event__slug=slug)
    except EventTeam.DoesNotExist:
        return 404, {'status': 'error', 'message': 'Team not found for this event'}

    try:
        crewmember = CrewMember.objects.get(
            id=data.crewmember_id, crew__event__slug=slug
        )
    except CrewMember.DoesNotExist:
        return 404, {
            'status': 'error',
            'message': 'Crew member not found for this event',
        }

    with transaction.atomic():
        team_member, _ = TeamMember.objects.update_or_create(
            event_team=event_team,
            crewmember=crewmember,
            defaults={'state': data.state},
        )
        clear_invalid_team_roles(event_team)

    return 200, {
        'event_team_id': str(event_team.id),
        'crewmember_id': str(crewmember.id),
        'state': team_member.state,
    }
