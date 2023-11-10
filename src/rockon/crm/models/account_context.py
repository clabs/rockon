from __future__ import annotations

from rockon.library.custom_model import CustomModel, models


class AccountContext(CustomModel):
    """AccountContext model."""

    slug = models.SlugField(max_length=1024)
    name = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.name:
            return self.name
        return self.slug

    class Meta:
        ordering = ["slug"]
