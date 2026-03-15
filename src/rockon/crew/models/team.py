from __future__ import annotations

from django.templatetags.static import static

from rockon.base.models import Event
from rockon.library import UploadToPathAndRename
from rockon.library.custom_model import CustomModel, models
from .team_category import TeamCategory


class Team(CustomModel):
    """Team model."""

    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(
        upload_to=UploadToPathAndRename('teams'),
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        TeamCategory,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='teams',
    )
    events = models.ManyToManyField(
        Event,
        blank=True,
        default=None,
        related_name='teams',
        through='rockoncrew.EventTeam',
    )
    contact_mail = models.EmailField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    show_teamlead = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('assets/4_3_placeholder.webp')
