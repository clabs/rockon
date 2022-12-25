from __future__ import annotations

from uuid import uuid4

from django.db import models

from event.models import Event

from .organisation import Organisation


class Person(models.Model):
    """Person model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    email = models.EmailField()
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    address_extension = models.CharField(max_length=255, null=True, blank=True)
    address_housenumber = models.SmallIntegerField(null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    place = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    internal_comment = models.TextField(null=True, blank=True)
    organisations = models.ManyToManyField(Organisation, blank=True)
    events = models.ManyToManyField(Event, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name"]
