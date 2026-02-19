from __future__ import annotations

from django.contrib.auth.models import User

from rockon.library.custom_model import CustomModel, models
from .attendance import Attendance
from .crew import Crew
from .shirt import Shirt
from .skill import Skill
from .team_category import TeamCategory


class CrewMemberStatus(models.TextChoices):
    UNKNOWN = 'unknown', 'Unbekannt'
    CONFIRMED = 'confirmed', 'Bestätigt'
    REJECTED = 'rejected', 'Abgelehnt'
    ARRIVED = 'arrived', 'Angekommen'


class CrewMemberNutrion(models.TextChoices):
    UNKNOWN = 'unknown', 'Unbekannt'
    VEGAN = 'vegan', 'Vegan'
    VEGETARIAN = 'vegetarian', 'Vegetarisch'
    OMNIVORE = 'omnivore', 'Omnivore'


class CrewMember(CustomModel):
    """Crewmember model."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crew = models.ForeignKey(
        Crew, on_delete=models.CASCADE, related_name='crew_members'
    )
    state = models.CharField(
        max_length=12,
        choices=CrewMemberStatus.choices,
        default=CrewMemberStatus.UNKNOWN,
        db_default=CrewMemberStatus.UNKNOWN,
    )
    shirt = models.ForeignKey(
        Shirt,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='crewmember_shirt',
    )
    nutrition = models.CharField(
        max_length=12,
        choices=CrewMemberNutrion.choices,
        default=CrewMemberNutrion.UNKNOWN,
        db_default=CrewMemberNutrion.UNKNOWN,
    )
    nutrition_note = models.TextField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    skills_note = models.TextField(null=True, blank=True)
    attendance = models.ManyToManyField(
        Attendance, blank=True, related_name='crew_members'
    )
    attendance_note = models.TextField(null=True, blank=True)
    stays_overnight = models.BooleanField(default=False, db_default=False)
    general_note = models.TextField(null=True, blank=True)
    needs_leave_of_absence = models.BooleanField(default=False)
    has_leave_of_absence = models.BooleanField(default=False)
    leave_of_absence_note = models.TextField(null=True, blank=True)
    internal_note = models.TextField(null=True, blank=True)
    interested_in = models.ManyToManyField(TeamCategory, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    # FIXME: this needs to move to profile model
    # def save(self, *args, **kwargs):
    #     if self.birthday is None:
    #         self.is_adult = None
    #         super().save(*args, **kwargs)
    #         return

    #     _birthday_as_datetime = make_aware(
    #         datetime(self.birthday.year, self.birthday.month, self.birthday.day)
    #     )
    #     self.is_adult = make_aware(datetime.now()) > _birthday_as_datetime + timedelta(
    #         days=365 * 18
    #     )
    #     super().save(*args, **kwargs)
