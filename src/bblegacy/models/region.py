from __future__ import annotations

from django.db import models

from bblegacy.helper import guid


class Region(models.Model):
    id = models.CharField(primary_key=True, max_length=255, default=guid)
    name = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Region"
        verbose_name_plural = "Regionen"
