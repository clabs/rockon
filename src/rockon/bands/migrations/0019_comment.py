# Generated by Django 5.1.4 on 2025-01-07 07:24

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rockonbands", "0018_alter_bandmedia_file"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
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
                ("text", models.TextField()),
                ("reason", models.TextField(blank=True, default=None, null=True)),
                (
                    "mood",
                    models.CharField(
                        blank=True, default=None, max_length=255, null=True
                    ),
                ),
                (
                    "band",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="rockonbands.band",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
                "abstract": False,
            },
        ),
    ]
