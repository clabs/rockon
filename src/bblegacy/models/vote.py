from __future__ import annotations

from django.db import models

from .bid import Bid
from .custom_model import CustomModel
from .user import User


class Vote(CustomModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="votes")
    rating = models.IntegerField()

    def __str__(self):
        return self.id

    class Meta:
        ordering = ["bid", "created"]
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
