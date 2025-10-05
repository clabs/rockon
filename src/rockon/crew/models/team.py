from __future__ import annotations

from django.contrib.auth.models import User
from django.templatetags.static import static

from rockon.library import UploadToPathAndRename
from rockon.library.custom_model import CustomModel, models

from .team_category import TeamCategory


class Team(CustomModel):
    """Team model."""

    name = models.CharField(max_length=255)
    description = models.TextField()
    lead = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='lead'
    )
    vize_lead = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='vize_lead',
    )
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
