from __future__ import annotations

from rockon.library.custom_model import CustomModel, models

from .crew_member import CrewMember
from .team import Team


class TeamMember(CustomModel):
    STATE = [
        ('unknown', 'Unbekannt'),
        ('confirmed', 'Bestätigt'),
        ('rejected', 'Abgelehnt'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    crewmember = models.ForeignKey(
        CrewMember, on_delete=models.CASCADE, related_name='teams'
    )
    state = models.CharField(max_length=12, choices=STATE, default='unknown')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.team.name
