from __future__ import annotations

from rockon.crew.models import EventTeam, TeamMember, TeamMemberState


def clear_invalid_team_roles(event_team: EventTeam) -> None:
    """Unset lead/vize_lead if they are no longer confirmed members of the team."""
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
