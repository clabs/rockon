from __future__ import annotations

from django.contrib.auth.models import User

from rockon.base.models import Event
from rockon.library.custom_model import CustomModel, models
from .team import Team


class EventTeam(CustomModel):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='team_links',
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='event_links',
    )
    lead = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='event_team_leads',
    )
    vize_lead = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='event_team_vize_leads',
    )

    class Meta:
        ordering = ('event__start', 'team__name')
        constraints = [
            models.UniqueConstraint(
                fields=('event', 'team'),
                name='crew_event_team_unique_assignment',
            )
        ]

    def __str__(self) -> str:
        return f'{self.team.name} ({self.event.name})'
