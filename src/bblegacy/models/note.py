from __future__ import annotations

from django.db import models

from .bid import Bid
from .custom_model import CustomModel
from .user import User


class Note(CustomModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="notes")
    type = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
