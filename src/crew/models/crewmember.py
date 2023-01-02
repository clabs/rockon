from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from django.db import models
from django.utils.timezone import make_aware

from crm.models import Person

from .attendance import Attendance
from .crew import Crew
from .shirt import Shirt
from .skill import Skill
from .team import Team


class CrewMember(models.Model):
    """Crewmember model."""

    NUTRION = [
        ("vegan", "Vegan"),
        ("vegetarian", "Vegetarisch"),
        ("omnivore", "Omnivor"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    birthday = models.DateField(null=True)
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE)
    shirt = models.ForeignKey(
        Shirt,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="crewmember_shirt",
    )
    nutrition = models.CharField(max_length=12, choices=NUTRION, null=True)
    nutrition_note = models.CharField(max_length=511, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    skills_note = models.CharField(max_length=1023, null=True, blank=True)
    attendance = models.ManyToManyField(Attendance, blank=True)
    attendance_note = models.CharField(max_length=1023, null=True, blank=True)
    overnight = models.BooleanField(default=False)
    teams = models.ManyToManyField(Team, blank=True)
    general_note = models.CharField(max_length=1023, null=True, blank=True)
    is_underaged = models.BooleanField(default=True, null=True)
    needs_leave_of_absence = models.BooleanField(default=False)
    has_leave_of_absence = models.BooleanField(default=False)
    leave_of_absence_note = models.CharField(max_length=1023, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person.first_name} {self.person.last_name}"

    def save(self, *args, **kwargs):
        if self.birthday is None:
            self.is_underaged = None
            super().save(*args, **kwargs)
            return

        _birthday_as_datetime = make_aware(
            datetime(self.birthday.year, self.birthday.month, self.birthday.day)
        )
        self.is_underaged = _birthday_as_datetime > make_aware(
            datetime.now()
        ) - timedelta(days=365 * 18)
        super().save(*args, **kwargs)
