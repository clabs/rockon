# Generated by Django 4.2.7 on 2023-11-11 11:24

from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LinkShortener",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("url", models.URLField()),
                ("slug", models.SlugField(unique=True)),
                ("comment", models.TextField()),
                ("counter", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ["created_at"],
                "abstract": False,
            },
        ),
    ]
