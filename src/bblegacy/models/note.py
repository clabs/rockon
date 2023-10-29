from __future__ import annotations

from django.db import models

from bblegacy.helper import guid

from .bid import Bid
from .user import User


class Note(models.Model):
    id = models.CharField(primary_key=True, max_length=255, default=guid)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="notes")
    type = models.CharField(max_length=255)
    text = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
