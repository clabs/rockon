from __future__ import annotations

from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models


class Organisation(models.Model):
    """Organisation model."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    org_name = models.CharField(max_length=255)
    org_address = models.CharField(max_length=511, null=True, default=None, blank=True)
    org_house_number = models.CharField(
        max_length=31, null=True, default=None, blank=True
    )
    org_address_extension = models.CharField(
        max_length=511, null=True, default=None, blank=True
    )
    org_zip = models.CharField(max_length=31, null=True, default=None, blank=True)
    org_place = models.CharField(max_length=255, null=True, default=None, blank=True)
    members = models.ManyToManyField(User, default=None, related_name="organisations")
    internal_comment = models.TextField(null=True, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.org_name

    class Meta:
        ordering = ["org_name"]
