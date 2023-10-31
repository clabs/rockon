from __future__ import annotations

from datetime import datetime

from django.db import models

from bblegacy.helper import guid

from .custom_model import CustomModel
from .user import User


def guid_proxy():
    return guid(48)


class Token(CustomModel):
    id = models.CharField(max_length=255, default=guid(30), primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"token:{self.user}"

    def update(self):
        self.timestamp = datetime.now()
        self.save()

    @classmethod
    def create(cls, user: User):
        return cls.objects.create(user=user, timestamp=datetime.now())
