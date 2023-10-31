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
        if self.name:
            return self.name
        return self.email

    class Meta:
        ordering = ["name"]

    def update_from_json(self, json: dict) -> User:
        self.name = json.get("name", self.name)
        self.email = json.get("email", self.email)
        self.password = json.get("password", self.password)
        self.provider = json.get("provider", self.provider)
        self.role = json.get("role", self.role)
        self.save()
        return self

    @classmethod
    def create_from_json(cls, json: dict) -> User:
        user = cls(
            name=json["name"],
            email=json["email"],
            password=json["password"],
            provider=json["provider"],
            role=json["role"],
        )
        user.save()
        return user
