from __future__ import annotations

from django.db import models

from .custom_model import CustomModel


class User(CustomModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    role = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
