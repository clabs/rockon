from __future__ import annotations

from django.contrib.auth.models import User

from rockon.library.custom_model import CustomModel, models

from .crew_date import CrewDate


class CrewDateResponseStatus(models.TextChoices):
    ATTENDING = 'attending', 'Zusage'
    TENTATIVE = 'tentative', 'Unsicher'
    UNAVAILABLE = 'unavailable', 'Absage'


class CrewDateResponse(CustomModel):
    """A crew member's RSVP status for a CrewDate."""

    crew_date = models.ForeignKey(
        CrewDate, on_delete=models.CASCADE, related_name='responses'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='crew_date_responses'
    )
    status = models.CharField(max_length=12, choices=CrewDateResponseStatus.choices)

    class Meta:
        unique_together = (('crew_date', 'user'),)

    def __str__(self):
        return f'{self.user} - {self.crew_date} - {self.status}'
