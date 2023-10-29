from __future__ import annotations

from django.db import models

from bblegacy.helper import guid

from .bid import Bid
from .user import User


class Vote(models.Model):
    id = models.CharField(primary_key=True, max_length=255, default=guid)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="votes")
    rating = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

    class Meta:
        ordering = ["bid", "created"]
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
