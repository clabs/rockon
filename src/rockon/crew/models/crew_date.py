from __future__ import annotations

from django.core.exceptions import ValidationError

from rockon.library.custom_model import CustomModel, models

from .crew import Crew


class CrewDate(CustomModel):
    """A scheduled crew date, e.g. a meeting or workshop day."""

    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, related_name='dates')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ('date', 'start_time')
        constraints = (
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F('start_time')),
                name='crew_date_end_after_start',
            ),
        )

    def __str__(self):
        return f'{self.title} ({self.date})'

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError('end_time must be after start_time.')
