from __future__ import annotations

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from event.models import Event
from library.custom_model import CustomModel, models

from .account_context import AccountContext


class UserProfile(CustomModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
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
    account_context = models.ManyToManyField(AccountContext, default=None, blank=True)

    def __str__(self):
        return self.user.username

    def is_profile_complete(self) -> bool:
        data_required = [
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.phone,
            self.address,
            self.address_housenumber,
            self.zip_code,
            self.place,
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
