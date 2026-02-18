from __future__ import annotations

from rockon.base.models import Event
from rockon.base.models.organisation import Organisation
from rockon.library.custom_model import CustomModel, models


def exhibitor_logo_path(instance, filename):
    """Upload path for exhibitor logos: exhibitors/<exhibitor_uuid>/<filename>"""
    return f'exhibitors/{instance.id}/{filename}'


class ExhibitorStatus(models.TextChoices):
    UNKNOWN = 'unknown', 'Unbekannt'
    CONTACTED = 'contacted', 'Kontakt aufgenommen'
    CONFIRMED = 'confirmed', 'Bestätigt'
    REJECTED = 'rejected', 'Abgelehnt'


class Exhibitor(CustomModel):
    """Exhibitor model."""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='exhibitors'
    )
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name='exhibitor'
    )
    state = models.CharField(
        max_length=12, choices=ExhibitorStatus.choices, default=ExhibitorStatus.UNKNOWN
    )
    market_id = models.CharField(
        max_length=255, default=None, null=True, blank=True, unique=True
    )
    general_note = models.TextField(null=True, default=None, blank=True)
    about_note = models.TextField(null=True, default=None, blank=True)
    offer_note = models.TextField(null=True, default=None, blank=True)
    website = models.URLField(
        max_length=500,
        null=True,
        default=None,
        blank=True,
        help_text='Internetadresse der Organisation oder des Angebots',
    )
    logo = models.FileField(
        upload_to=exhibitor_logo_path,
        null=True,
        default=None,
        blank=True,
        help_text='Logo oder Bild des Ausstellers (JPG, PNG, EPS oder PDF)',
    )
    internal_comment = models.TextField(null=True, default=None, blank=True)

    def __str__(self):
        return self.organisation.org_name
