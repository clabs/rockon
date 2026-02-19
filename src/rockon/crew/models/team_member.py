from __future__ import annotations

from rockon.library.custom_model import CustomModel, models
from .crew_member import CrewMember
from .team import Team


class TeamMemberState(models.TextChoices):
    UNKNOWN = 'unknown', 'Unbekannt'
    CONFIRMED = 'confirmed', 'Bestätigt'
    REJECTED = 'rejected', 'Abgelehnt'


class TeamMember(CustomModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    crewmember = models.ForeignKey(
        CrewMember, on_delete=models.CASCADE, related_name='teams'
    )
    state = models.CharField(
        max_length=12,
        choices=TeamMemberState.choices,
        default=TeamMemberState.UNKNOWN,
        db_default=TeamMemberState.UNKNOWN,
    )

    def __str__(self) -> str:
        return self.team.name
