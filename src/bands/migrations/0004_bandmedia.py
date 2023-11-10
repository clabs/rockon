# Generated by Django 4.2.7 on 2023-11-08 12:16

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bands", "0003_band_bid_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="BandMedia",
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
                (
                    "media_type",
                    models.CharField(
                        choices=[
                            ("unknown", "Unbekannt"),
                            ("document", "Dokument"),
                            ("audio", "Audio"),
                            ("link", "Link"),
                            ("press_photo", "Pressefoto"),
                            ("logo", "Logo"),
                        ],
                        default="unknown",
                        max_length=32,
                    ),
                ),
                ("url", models.URLField(blank=True, default=None, null=True)),
                (
                    "file",
                    models.FileField(blank=True, default=None, null=True, upload_to=""),
                ),
                (
                    "thumbnail",
                    models.ImageField(
                        blank=True, default=None, null=True, upload_to=""
                    ),
                ),
                (
                    "file_name_original",
                    models.CharField(
                        blank=True, default=None, max_length=512, null=True
                    ),
                ),
                (
                    "band",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="media",
                        to="bands.band",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
                "abstract": False,
            },
        ),
    ]