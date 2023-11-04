from __future__ import annotations

from library.custom_model import CustomModel, models


class Skill(CustomModel):
    """Skill model."""

    name = models.CharField(max_length=255)
    explanation = models.CharField(max_length=511)
    icon = models.CharField(
        max_length=255,
        help_text='<a target="_blank" href="https://fontawesome.com/search?m=free&o=r">Wähle ein Icon aus</a>',
        default='<i class="fa-solid fa-heart"></i>',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
