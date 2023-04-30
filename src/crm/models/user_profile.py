from __future__ import annotations

from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from event.models import Event


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
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
    contact_mail = models.EmailField(
        max_length=1024, null=True, default=None, blank=True
    )
    comment = models.TextField(null=True, default=None, blank=True)
    internal_comment = models.TextField(null=True, default=None, blank=True)
    events = models.ManyToManyField(Event, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
