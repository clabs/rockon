from __future__ import annotations

from datetime import datetime

import pytz
from django.db import models

from bblegacy.helper import guid


class CustomModel(models.Model):
    id = models.CharField(primary_key=True, max_length=255, default=guid)
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        abstract = True

    # Because we can not overwrite auto_now_add in Django
    # https://code.djangoproject.com/ticket/16583
    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = datetime.now(pytz.utc)
        if self.modified is None:
            self.modified = datetime.now(pytz.utc)
        super().save(*args, **kwargs)
