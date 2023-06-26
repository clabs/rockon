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
from .team_category import TeamCategory


class CrewMemberStatus(models.TextChoices):
    UNKNOWN = "unknown", "Unbekannt"
    CONFIRMED = "confirmed", "Bestätigt"
    REJECTED = "rejected", "Abgelehnt"
    ARRIVED = "arrived", "Angekommen"


class CrewMemberNutrion(models.TextChoices):
    UNKNOWN = "unknown", "Unbekannt"
    VEGAN = "vegan", "Vegan"
    VEGETARIAN = "vegetarian", "Vegetarisch"
    OMNIVORE = "omnivore", "Omnivor"


class CrewMember(models.Model):
    """Crewmember model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True)
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE)
    state = models.CharField(
        max_length=12,
        choices=CrewMemberStatus.choices,
        default=CrewMemberStatus.UNKNOWN,
    )
    shirt = models.ForeignKey(
        Shirt,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="crewmember_shirt",
    )
    nutrition = models.CharField(
        max_length=12,
        choices=CrewMemberNutrion.choices,
        default=CrewMemberNutrion.UNKNOWN,
    )
    nutrition_note = models.TextField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    skills_note = models.TextField(null=True, blank=True)
    attendance = models.ManyToManyField(
        Attendance, blank=True, related_name="crew_members"
    )
    attendance_note = models.TextField(null=True, blank=True)
    stays_overnight = models.BooleanField(default=False)
    general_note = models.TextField(null=True, blank=True)
    is_adult = models.BooleanField(default=False)
    needs_leave_of_absence = models.BooleanField(default=False)
    has_leave_of_absence = models.BooleanField(default=False)
    leave_of_absence_note = models.TextField(null=True, blank=True)
    internal_note = models.TextField(null=True, blank=True)
    interested_in = models.ManyToManyField(TeamCategory, blank=True)
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
