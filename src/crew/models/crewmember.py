from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import make_aware

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

    STATE = [
        ("unknown", "Unbekannt"),
        ("confirmed", "Bestätigt"),
        ("rejected", "Abgelehnt"),
        ("arrived", "Angekommen"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True)
    crew = models.OneToOneField(Crew, on_delete=models.CASCADE)
    state = models.CharField(max_length=12, choices=STATE, default="unknown")
    shirt = models.OneToOneField(
        Shirt,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="crewmember_shirt",
    )
    nutrition = models.CharField(max_length=12, choices=NUTRION, null=True)
    nutrition_note = models.TextField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    skills_note = models.TextField(null=True, blank=True)
    attendance = models.ManyToManyField(Attendance, blank=True)
    attendance_note = models.TextField(null=True, blank=True)
    stays_overnight = models.BooleanField(default=False)
    teams = models.ManyToManyField(Team, blank=True)
    general_note = models.TextField(null=True, blank=True)
    is_adult = models.BooleanField(default=False)
    needs_leave_of_absence = models.BooleanField(default=False)
    has_leave_of_absence = models.BooleanField(default=False)
    leave_of_absence_note = models.TextField(null=True, blank=True)
    internal_note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        if self.birthday is None:
            self.is_adult = None
            super().save(*args, **kwargs)
            return

        _birthday_as_datetime = make_aware(
            datetime(self.birthday.year, self.birthday.month, self.birthday.day)
        )
        self.is_adult = make_aware(datetime.now()) > _birthday_as_datetime + timedelta(
            days=365 * 18
        )
        super().save(*args, **kwargs)
