from __future__ import annotations

from rockon.library.custom_model import CustomModel, models


class Asset(CustomModel):
    """Asset model."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_bool = models.BooleanField(default=False)
    icon = models.CharField(
        default='<i class="fa-solid fa-heart"></i>',
        help_text='<a target="_blank" href="https://fontawesome.com/search?m=free&o=r">Wähle ein Icon aus</a>',
        max_length=255,
    )
    internal_comment = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
