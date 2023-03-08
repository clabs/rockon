from __future__ import annotations

from uuid import uuid4

from django.db import models

from crm.models.organisation import Organisation
from event.models import Event


class Exhibitor(models.Model):
    """Exhibitor model."""

    STATE = [
        ("unknown", "Unbekannt"),
        ("contacted", "Kontakt aufgenommen"),
        ("rejected", "Abgelehnt"),
        ("confirmed", "Bestätigt"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="exhibitors"
    )
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="exhibitor"
    )
    state = models.CharField(max_length=12, choices=STATE, default="unknown")
    market_id = models.CharField(max_length=255, default=None, null=True, unique=True)
    general_note = models.TextField(null=True, default=None)
    internal_comment = models.TextField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organisation.org_name
