from __future__ import annotations

from rockon.library.custom_model import CustomModel, models
from .crew_member import CrewMember
from .event_team import EventTeam


class TeamMemberState(models.TextChoices):
    UNKNOWN = 'unknown', 'Unbekannt'
    CONFIRMED = 'confirmed', 'Bestätigt'
    REJECTED = 'rejected', 'Abgelehnt'


class TeamMember(CustomModel):
    event_team = models.ForeignKey(
        EventTeam,
        on_delete=models.CASCADE,
        related_name='members',
    )
    crewmember = models.ForeignKey(
        CrewMember, on_delete=models.CASCADE, related_name='teams'
    )
    state = models.CharField(
        max_length=12,
        choices=TeamMemberState.choices,
        default=TeamMemberState.UNKNOWN,
        db_default=TeamMemberState.UNKNOWN,
    )

    @property
    def team(self):
        return self.event_team.team

    @property
    def event(self):
        return self.event_team.event

    def __str__(self) -> str:
        return self.event_team.team.name
