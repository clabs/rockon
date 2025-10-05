from __future__ import annotations

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from rockon.base.models import Event
from rockon.library.custom_model import CustomModel, models


class UserProfile(CustomModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        unique=True,
    )
    nick_name = models.CharField(max_length=255, null=True, default=None, blank=True)
    email_is_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=255, null=True, default=None, blank=True)
    address = models.CharField(max_length=255, null=True, default=None, blank=True)
    address_extension = models.CharField(
        max_length=255, null=True, default=None, blank=True
    )
    address_housenumber = models.CharField(
        max_length=255, null=True, default=None, blank=True
    )
    zip_code = models.CharField(max_length=255, null=True, default=None, blank=True)
    place = models.CharField(max_length=255, null=True, default=None, blank=True)
    comment = models.TextField(null=True, default=None, blank=True)
    birthday = models.DateField(null=True, default=None, blank=True)
    internal_comment = models.TextField(null=True, default=None, blank=True)
    events = models.ManyToManyField(Event, default=None, blank=True)

    def __str__(self):
        if self.user.username:
            return self.user.username
        if self.user.email:
            return self.user.email
        return f'username:{self.user.username}'

    @property
    def full_name(self) -> str:
        """Return the full name of the user."""
        full_name = f'{self.user.first_name} {self.user.last_name}'
        if not full_name.strip():
            full_name = self.user.email
        if not full_name.strip():
            full_name = self.user.username
        return full_name

    def is_profile_complete_crew(self) -> bool:
        """Check if user profile is complete for crew signup."""
        data_required = [
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.phone,
            self.address,
            self.address_housenumber,
            self.zip_code,
            self.place,
            self.birthday,
        ]

        if all(data_required):
            return True

        return False

    def is_profile_complete_band(self) -> bool:
        """Check if user profile is complete for band application."""
        data_required = [
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.phone,
        ]

        if all(data_required):
            return True

        return False

    def is_profile_complete_exhibitor(self) -> bool:
        """Check if user profile is complete for exhibitor application."""
        data_required = [
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.phone,
        ]

        if all(data_required):
            return True

        return False


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
